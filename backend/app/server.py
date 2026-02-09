import logging
from typing import AsyncIterator, Any
from datetime import datetime

from agents import Runner
from chatkit.server import ChatKitServer
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from chatkit.types import (
    ThreadMetadata,
    UserMessageItem,
    ThreadStreamEvent,
    ThreadItemDoneEvent,
    AssistantMessageItem,
    AssistantMessageContent,
    Action,
    WidgetItem,
    HiddenContextItem,
    ThreadItemReplacedEvent,
)

from app.types import RequestContext
from app.store.chat_store import SqliteChatStore
from app.store.app_store import create_event, get_contacts_by_ids
from app.agents.scheduler import scheduler_agent
from app.widgets.builders import build_meeting_confirmed, build_selection_locked # Import the new builder

logger = logging.getLogger(__name__)


class MeetingSchedulerServer(ChatKitServer[RequestContext]):
    def __init__(self):
        super().__init__(store=SqliteChatStore())

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        # 1. Load History
        items_page = await self.store.load_thread_items(
            thread.id, after=None, limit=20, order="desc", context=context
        )
        # Reverse to get chronological order for the model
        items = list(reversed(items_page.data))

        # 2. Convert to Agent Input
        # Note: simple_to_agent_input automatically handles standard items.
        # HiddenContextItems created in action() will be seen by the model here.
        input_items = await simple_to_agent_input(items)

        # 3. Create Context
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

        # 4. Run Agent
        result = Runner.run_streamed(
            scheduler_agent, input_items, context=agent_context
        )

        # 5. Stream Events
        async for event in stream_agent_response(agent_context, result):
            yield event

    async def action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """
        The State Machine. Handles UI interactions.
        """
        logger.info(f"Action received: {action.type} with payload: {action.payload}")

        if action.type == "contacts.confirm":
            selected_map = action.payload.get("selected", {})
            if not isinstance(selected_map, dict):
                # Fallback in case of flat payload (depends on specific SDK version/config)
                selected_ids = [
                    key.replace("selected.", "") 
                    for key, val in action.payload.items() 
                    if key.startswith("selected.") and val is True
                ]
            else:
                # Standard nested behavior
                selected_ids = [
                    contact_id for contact_id, is_selected in selected_map.items() 
                    if is_selected is True
                ]
            
            if not selected_ids:
                yield ThreadItemDoneEvent(
                    item=AssistantMessageItem(
                        id=self.store.generate_item_id("message", thread, context),
                        thread_id=thread.id,
                        created_at=datetime.now(),
                        content=[AssistantMessageContent(text="No contacts selected. Please check at least one box.")]
                    )
                )
                return

            # 1. Resolve names
            contacts = await get_contacts_by_ids(selected_ids)
            names = ", ".join([c.name for c in contacts])

            # 2. LOCK THE WIDGET (Prevent re-clicking)
            if sender:
                locked_widget = build_selection_locked(
                    title="Attendees Confirmed",
                    detail=f"{len(contacts)} selected: {names}"
                )
                # Reuse sender ID to replace in-place
                new_item = sender.model_copy(update={"widget": locked_widget})
                yield ThreadItemReplacedEvent(item=new_item)

            # 3. Inject Hidden Context for the LLM
            hidden_item = HiddenContextItem(
                id=self.store.generate_item_id("hidden_context_item", thread, context),
                thread_id=thread.id,
                created_at=datetime.now(),
                content=f"<USER_ACTION>User confirmed selection of contacts: {names} (IDs: {selected_ids})</USER_ACTION>"
            )
            await self.store.add_thread_item(thread.id, hidden_item, context)

            # 4. Trigger Agent Response (Agent will now see the hidden context and call find_availability)
            async for event in self.respond(thread, None, context):
                yield event

        # --- TIME SLOT SELECTION---
        elif action.type == "schedule.pick_slot":
            slot_id = action.payload.get("slot_id")
            time_label = action.payload.get("time_label", "Selected Slot")

            # 1. LOCK THE WIDGET
            if sender:
                locked_widget = build_selection_locked(
                    title="Time Selected",
                    detail=time_label
                )
                new_item = sender.model_copy(update={"widget": locked_widget})
                yield ThreadItemReplacedEvent(item=new_item)

            # 2. Inject Hidden Context
            hidden_item = HiddenContextItem(
                id=self.store.generate_item_id("hidden_context_item", thread, context),
                thread_id=thread.id,
                created_at=datetime.now(),
                content=f"<USER_ACTION>User selected time slot ID: {slot_id} ({time_label})</USER_ACTION>"
            )
            await self.store.add_thread_item(thread.id, hidden_item, context)

            # 3. Trigger Agent Response (Agent will now call draft_invite)
            async for event in self.respond(thread, None, context):
                yield event

        # --- REVISION REQUEST ---
        elif action.type == "invite.request_revision":
            # Note: We usually DON'T lock the form here, so the user can see what they are editing contextually,
            # OR we lock it to force them to wait for the new form. Let's lock it to be safe.
            if sender:
                locked_widget = build_selection_locked(
                    title="Action",
                    detail="Requested Changes"
                )
                new_item = sender.model_copy(update={"widget": locked_widget})
                yield ThreadItemReplacedEvent(item=new_item)

            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    id=self.store.generate_item_id("message", thread, context),
                    thread_id=thread.id,
                    created_at=datetime.now(),
                    content=[
                        AssistantMessageContent(
                            text="No problem. What specific changes would you like to make to the subject or agenda?"
                        )
                    ],
                )
            )

        # --- FINAL SEND ---
        elif action.type == "invite.send":
            p = action.payload or {}

            # 1. Write to DB
            await create_event(
                organizer_id=context.user_id,
                subject=p.get("subject", "No Subject"),
                agenda=p.get("agenda", ""),
                location=p.get("location", "Zoom"),
                attendees=p.get("attendees", "Unknown Attendees"),
                time_str=p.get("time_str", "Unknown Time"),
            )

            # 2. Replace the Editable Widget with a Static Confirmation Widget
            if sender:
                confirmed_widget = build_meeting_confirmed(
                    subject=p.get("subject", "Meeting Scheduled"), 
                    time_str=p.get("time_str", "Selected Time")
                )

                new_item = sender.model_copy(update={"widget": confirmed_widget})
                yield ThreadItemReplacedEvent(item=new_item)

            # 3. Confirmation Message
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    id=self.store.generate_item_id("message", thread, context),
                    thread_id=thread.id,
                    created_at=datetime.now(),
                    content=[
                        AssistantMessageContent(text="Invitation sent successfully!")
                    ],
                )
            )