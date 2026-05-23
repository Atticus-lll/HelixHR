from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.config import settings

engine = create_engine(
    settings.database_url,
    echo=settings.app.debug,
    poolclass=NullPool,
    connect_args={
        "init_command": "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci",
        "connect_timeout": 10,
    },
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
