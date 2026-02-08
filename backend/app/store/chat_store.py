import json
from typing import Any
from chatkit.store import Store, NotFoundError
from chatkit.types import ThreadMetadata, ThreadItem, Page
from app.database import get_db_connection
from app.types import RequestContext


class SqliteChatStore(Store[RequestContext]):
    async def load_thread(
        self, thread_id: str, context: RequestContext
    ) -> ThreadMetadata:
        async with get_db_connection() as db:
            async with db.execute(
                "SELECT data FROM threads WHERE id = ? AND user_id = ?",
                (thread_id, context.user_id),
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise NotFoundError(f"Thread {thread_id} not found")
                return ThreadMetadata.model_validate(json.loads(row[0]))

    async def save_thread(
        self, thread: ThreadMetadata, context: RequestContext
    ) -> None:
        async with get_db_connection() as db:
            data = thread.model_dump_json()
            await db.execute(
                """
                INSERT INTO threads (id, user_id, created_at, data) 
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET data = excluded.data
                """,
                (thread.id, context.user_id, thread.created_at.isoformat(), data),
            )
            await db.commit()

    async def load_threads(
        self, limit: int, after: str | None, order: str, context: RequestContext
    ) -> Page[ThreadMetadata]:
        async with get_db_connection() as db:
            query = "SELECT data FROM threads WHERE user_id = ? ORDER BY created_at DESC LIMIT ?"
            params = [context.user_id, limit]

            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                data = [
                    ThreadMetadata.model_validate(json.loads(row[0])) for row in rows
                ]

        return Page(data=data, has_more=False)

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: RequestContext,
    ) -> Page[ThreadItem]:
        async with get_db_connection() as db:
            query = "SELECT data FROM items WHERE thread_id = ? ORDER BY created_at DESC LIMIT ?"
            async with db.execute(query, (thread_id, limit)) as cursor:
                rows = await cursor.fetchall()
                data = [ThreadItem.model_validate(json.loads(row[0])) for row in rows]
                if order == "asc":
                    data.reverse()

        return Page(data=data, has_more=False)

    async def add_thread_item(
        self, thread_id: str, item: ThreadItem, context: RequestContext
    ) -> None:
        async with get_db_connection() as db:
            data = item.model_dump_json()
            await db.execute(
                "INSERT INTO items (id, thread_id, user_id, created_at, data) VALUES (?, ?, ?, ?, ?)",
                (
                    item.id,
                    thread_id,
                    context.user_id,
                    item.created_at.isoformat(),
                    data,
                ),
            )
            await db.commit()

    async def save_item(
        self, thread_id: str, item: ThreadItem, context: RequestContext
    ) -> None:
        async with get_db_connection() as db:
            data = item.model_dump_json()
            await db.execute(
                """
                INSERT INTO items (id, thread_id, user_id, created_at, data) 
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET data = excluded.data
                """,
                (
                    item.id,
                    thread_id,
                    context.user_id,
                    item.created_at.isoformat(),
                    data,
                ),
            )
            await db.commit()

    async def load_item(
        self, thread_id: str, item_id: str, context: RequestContext
    ) -> ThreadItem:
        async with get_db_connection() as db:
            async with db.execute(
                "SELECT data FROM items WHERE id = ? AND thread_id = ?",
                (item_id, thread_id),
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise NotFoundError(f"Item {item_id} not found")
                return ThreadItem.model_validate(json.loads(row[0]))

    async def delete_thread(self, thread_id: str, context: RequestContext) -> None:
        async with get_db_connection() as db:
            await db.execute("DELETE FROM threads WHERE id = ?", (thread_id,))
            await db.commit()

    async def delete_thread_item(
        self, thread_id: str, item_id: str, context: RequestContext
    ) -> None:
        async with get_db_connection() as db:
            await db.execute(
                "DELETE FROM items WHERE id = ? AND thread_id = ?", (item_id, thread_id)
            )
            await db.commit()

    # Attachments not implemented for Phase 1
    async def save_attachment(self, attachment: Any, context: RequestContext) -> None:
        NotImplementedError("Attachment handling not implemented yet")

    async def load_attachment(self, attachment_id: str, context: RequestContext) -> Any:
        NotImplementedError("Attachment handling not implemented yet")

    async def delete_attachment(
        self, attachment_id: str, context: RequestContext
    ) -> None:
        NotImplementedError("Attachment handling not implemented yet")