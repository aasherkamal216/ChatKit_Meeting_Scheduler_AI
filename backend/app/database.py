import aiosqlite
from pathlib import Path
from contextlib import asynccontextmanager

# Ensure this path resolves correctly relative to where you run the script
DB_PATH = Path(__file__).parent.parent / "chatkit.db"

async def get_db_path() -> str:
    return str(DB_PATH)

@asynccontextmanager
async def get_db_connection():
    """
    Yields a database connection that closes automatically on exit.
    """
    conn = await aiosqlite.connect(DB_PATH)
    conn.row_factory = aiosqlite.Row
    try:
        yield conn
    finally:
        await conn.close()