"""Database configuration with hybrid SQLite/PostgreSQL support"""
from sqlalchemy import create_engine, String, JSON
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import AsyncGenerator, Generator
from api.config import settings

# Detect database mode
IS_SQLITE = settings.database_url.startswith("sqlite")
IS_POSTGRES = settings.database_url.startswith("postgresql")

# Base class for models (shared by both modes)
Base = declarative_base()

if IS_SQLITE:
    # ===== SQLite Mode (Synchronous) =====

    # Create sync engine
    engine = create_engine(
        settings.database_url,
        echo=settings.app_env == "development",
        connect_args={"check_same_thread": False}  # Allow multi-threading
    )

    # Create sync session maker
    SessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False
    )

    def get_db() -> Generator:
        """Dependency to get database session (sync)"""
        db = SessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def init_db():
        """Initialize database tables (sync)"""
        Base.metadata.create_all(engine)
        print("[OK] SQLite database initialized")

else:
    # ===== PostgreSQL Mode (Asynchronous) =====

    # Create async engine
    engine = create_async_engine(
        settings.database_url,
        echo=settings.app_env == "development",
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

    # Create async session maker
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async def get_db() -> AsyncGenerator:
        """Dependency to get database session (async)"""
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def init_db():
        """Initialize database tables (async)"""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("[OK] PostgreSQL database initialized")


# Cross-database type helpers
def UUID(as_uuid=False):
    """
    Cross-database UUID type
    - SQLite: Uses String(36)
    - PostgreSQL: Uses native UUID type
    """
    if IS_SQLITE:
        return String(36)
    else:
        from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
        return PostgresUUID(as_uuid=as_uuid)

def ARRAY(item_type):
    """
    Cross-database ARRAY type
    - SQLite: Uses JSON (stored as text)
    - PostgreSQL: Uses native ARRAY type
    """
    if IS_SQLITE:
        return JSON
    else:
        from sqlalchemy.dialects.postgresql import ARRAY as PostgresARRAY
        return PostgresARRAY(item_type)

# JSONB helper (PostgreSQL JSONB → SQLite JSON)
if IS_SQLITE:
    JSONB = JSON
else:
    from sqlalchemy.dialects.postgresql import JSONB
