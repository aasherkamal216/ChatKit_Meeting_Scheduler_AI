from typing import AsyncIterator, Any
from datetime import datetime
from chatkit.server import ChatKitServer
from chatkit.types import (
    ThreadMetadata,
    UserMessageItem,
    ThreadStreamEvent,
    ThreadItemDoneEvent,
    AssistantMessageItem,
    AssistantMessageContent,
    Action,
    WidgetItem,
)
from app.types import RequestContext
from app.store.chat_store import SqliteChatStore


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
        Phase 1 Echo Implementation.
        """
        # Echo response for testing Phase 1
        yield ThreadItemDoneEvent(
            item=AssistantMessageItem(
                id=self.store.generate_item_id("message", thread, context),
                thread_id=thread.id,
                created_at=datetime.now(),
                content=[
                    AssistantMessageContent(
                        text=f"Hello User {context.user_id}! System is ready. You said: {input_user_message.content[0].text if input_user_message else 'Nothing'}"
                    )
                ],
            )
        )

    async def action(
        self,
        thread: ThreadMetadata,
        action: Action[str, Any],
        sender: WidgetItem | None,
        context: RequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        # Placeholder for Phase 4
        yield ThreadItemDoneEvent(
            item=AssistantMessageItem(
                id=self.store.generate_item_id("message", thread, context),
                thread_id=thread.id,
                created_at=datetime.now(),
                content=[
                    AssistantMessageContent(text=f"Action received: {action.type}")
                ],
            )
        )