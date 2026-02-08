import logging
from app.database import get_db_connection

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
    # FIXED: usage of async context manager
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
            contacts = [
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
            await db.executemany(
                "INSERT INTO contacts (id, owner_id, name, email, role, avatar_url) VALUES (?, ?, ?, ?, ?, ?)",
                contacts,
            )
            await db.commit()