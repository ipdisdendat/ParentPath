"""Initialize ParentPath database (SQLite or PostgreSQL)"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.database import Base, engine, init_db, IS_SQLITE, IS_POSTGRES
from api.models import Parent, Child, Subscription, Item, Card, Newsletter, MessageLog, Ticket


def main():
    """Initialize database tables"""
    print("ParentPath Database Initialization")
    print("=" * 50)

    if IS_SQLITE:
        print(f"Mode: SQLite (sync)")
        print(f"Database: parentpath.db")
        print()

        # Synchronous initialization
        init_db()

        # List tables
        tables = list(Base.metadata.tables.keys())
        print(f"Tables created: {len(tables)}")
        for table in tables:
            print(f"  - {table}")

    elif IS_POSTGRES:
        print(f"Mode: PostgreSQL (async)")
        print()

        # Asynchronous initialization
        async def async_init():
            await init_db()

            # List tables
            tables = list(Base.metadata.tables.keys())
            print(f"Tables created: {len(tables)}")
            for table in tables:
                print(f"  - {table}")

        asyncio.run(async_init())

    else:
        print("❌ Unknown database type")
        print(f"   DATABASE_URL must start with 'sqlite://' or 'postgresql://'")
        sys.exit(1)

    print()
    print("✅ Database initialization complete!")
    print()
    print("Next steps:")
    print("  1. Start API: uvicorn api.main:app --reload")
    print("  2. Test health: curl http://localhost:8000/health")


if __name__ == "__main__":
    main()
