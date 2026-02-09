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
from app.widgets.builders import build_meeting_confirmed

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
        """
        Main inference loop. Runs the Agent against the thread history.
        """
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
            # Payload e.g.: {"selected.c1": True, "selected.c2": True}
            selected_ids = [
                key.replace("selected.", "")
                for key, val in action.payload.items()
                if key.startswith("selected.") and val is True
            ]

            # Resolve names for better context
            contacts = await get_contacts_by_ids(selected_ids)
            names = ", ".join([c.name for c in contacts])

            # Inject Hidden Context so Agent knows what happened
            hidden_item = HiddenContextItem(
                id=self.store.generate_item_id("hidden_context_item", thread, context),
                thread_id=thread.id,
                created_at=datetime.now(),
                content=f"<USER_ACTION>User confirmed selection of contacts: {names} (IDs: {selected_ids})</USER_ACTION>",
            )
            await self.store.add_thread_item(thread.id, hidden_item, context)

            # Trigger Agent Response (Agent will likely see this and call find_availability)
            async for event in self.respond(thread, None, context):
                yield event

        elif action.type == "schedule.pick_slot":
            slot_id = action.payload.get("slot_id")

            # Inject Hidden Context
            hidden_item = HiddenContextItem(
                id=self.store.generate_item_id("hidden_context_item", thread, context),
                thread_id=thread.id,
                created_at=datetime.now(),
                content=f"<USER_ACTION>User clicked/selected time slot ID: {slot_id}</USER_ACTION>",
            )
            await self.store.add_thread_item(thread.id, hidden_item, context)

            # Trigger Agent Response (Agent will likely call draft_invite)
            async for event in self.respond(thread, None, context):
                yield event

        elif action.type == "invite.request_revision":
            # HITL Flow: User wants to change something via text.
            # We DO NOT call respond() here. We yield a message asking for details.
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
            # Flow stops. Waiting for UserMessageItem input in next turn.

        elif action.type == "invite.send":
            # Finalization Flow.
            # The payload contains the FORM data (subject, agenda, etc)
            p = action.payload

            # 1. Write to DB
            await create_event(
                organizer_id=context.user_id,
                subject=p.get("subject"),
                agenda=p.get("agenda"),
                location=p.get("location"),
                attendees=p.get("attendees"),
                time_str=p.get("time_str"),
            )

            # 2. Replace the Editable Widget with a Static Confirmation Widget
            if sender:
                confirmed_widget = build_meeting_confirmed(
                    subject=p.get("subject"), time_str=p.get("time_str")
                )

                # We reuse the sender ID to replace it in-place
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
