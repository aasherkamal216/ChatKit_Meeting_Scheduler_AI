import logging
from typing import List
import uuid

from app.database import get_db_connection
from app.types import Contact

logger = logging.getLogger(__name__)


async def init_db():
    # FIXED: usage of async context manager
    async with get_db_connection() as db:
        # Business Tables
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL
            )
        """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS contacts (
                id TEXT PRIMARY KEY,
                owner_id TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                role TEXT NOT NULL,
                avatar_url TEXT,
                FOREIGN KEY(owner_id) REFERENCES users(id)
            )
        """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                organizer_id TEXT NOT NULL,
                subject TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                attendees TEXT NOT NULL,
                location TEXT,
                agenda TEXT,
                status TEXT DEFAULT 'confirmed',
                FOREIGN KEY(organizer_id) REFERENCES users(id)
            )
        """
        )

        # ChatKit Tables
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS threads (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                data JSON NOT NULL
            )
        """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                thread_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                data JSON NOT NULL,
                FOREIGN KEY(thread_id) REFERENCES threads(id) ON DELETE CASCADE
            )
        """
        )
        await db.commit()


async def seed_db():
    async with get_db_connection() as db:
        # Check if users exist
        async with db.execute("SELECT count(*) FROM users") as cursor:
            row = await cursor.fetchone()
            count = row[0]

        if count == 0:
            logger.info("Seeding database...")
            # Users
            await db.execute(
                "INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
                ("alice", "Alice Executive", "alice@example.com"),
            )
            await db.execute(
                "INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
                ("bob", "Bob Manager", "bob@example.com"),
            )

            # Contacts for Alice
            alice_contacts = [
                (
                    "c1",
                    "alice",
                    "Bob Manager",
                    "bob@example.com",
                    "Product Manager",
                    "https://i.pravatar.cc/150?u=bob",
                ),
                (
                    "c2",
                    "alice",
                    "Charlie Designer",
                    "charlie@example.com",
                    "Lead Designer",
                    "https://i.pravatar.cc/150?u=charlie",
                ),
                (
                    "c3",
                    "alice",
                    "Dana Engineer",
                    "dana@example.com",
                    "CTO",
                    "https://i.pravatar.cc/150?u=dana",
                ),
            ]

            # Contacts for Bob (NEW)
            bob_contacts = [
                (
                    "c4",
                    "bob",
                    "Alice Executive",
                    "alice@example.com",
                    "Boss",
                    "https://i.pravatar.cc/150?u=alice",
                ),
                (
                    "c5",
                    "bob",
                    "Eve External",
                    "eve@vendor.com",
                    "Vendor",
                    "https://i.pravatar.cc/150?u=eve",
                ),
            ]

            await db.executemany(
                "INSERT INTO contacts (id, owner_id, name, email, role, avatar_url) VALUES (?, ?, ?, ?, ?, ?)",
                alice_contacts + bob_contacts,
            )
            await db.commit()


# --- Helper functions for contacts ---
async def search_contacts_in_db(owner_id: str, query: str) -> List[Contact]:
    async with get_db_connection() as db:
        # Use LOWER() for case-insensitive matching in SQLite
        sql = """
            SELECT * FROM contacts 
            WHERE owner_id = ? 
            AND (LOWER(name) LIKE LOWER(?) OR LOWER(email) LIKE LOWER(?))
        """
        search_term = f"%{query}%"
        async with db.execute(sql, (owner_id, search_term, search_term)) as cursor:
            rows = await cursor.fetchall()
            return [Contact(**dict(row)) for row in rows]


async def get_contacts_by_ids(ids: List[str]) -> List[Contact]:
    async with get_db_connection() as db:
        placeholders = ", ".join(["?"] * len(ids))
        sql = f"SELECT * FROM contacts WHERE id IN ({placeholders})"
        async with db.execute(sql, ids) as cursor:
            rows = await cursor.fetchall()
            return [Contact(**dict(row)) for row in rows]


async def create_event(
    organizer_id: str,
    subject: str,
    agenda: str,
    location: str,
    attendees: str,
    time_str: str,
) -> str:
    async with get_db_connection() as db:
        event_id = str(uuid.uuid4())
        # In a real app, you'd parse time_str to actual datetime objects.
        # For this demo, we store strings to match the simplified widget data.
        await db.execute(
            """
            INSERT INTO events (id, organizer_id, subject, agenda, location, attendees, start_time, end_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                organizer_id,
                subject,
                agenda,
                location,
                attendees,
                time_str,
                time_str,
            ),
        )
        await db.commit()
        return event_id
