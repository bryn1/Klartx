"""
KlartX — Database connection and session management
Contract ID: @db/session/engine
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# vm106 runs the app from a read-only dir (ProtectSystem=strict); systemd's writable StateDirectory
# arrives as $STATE_DIRECTORY. Locally (unset) the DB stays at ./klartx.db as before.
_STATE_DIR = os.environ.get("STATE_DIRECTORY", "").split(":")[0]
DATABASE_URL = os.environ.get(
    "KLARTX_DATABASE_URL",
    f"sqlite:///{os.path.join(_STATE_DIR, 'klartx.db')}" if _STATE_DIR else "sqlite:///klartx.db",
)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_session():
    """Yield a new database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
