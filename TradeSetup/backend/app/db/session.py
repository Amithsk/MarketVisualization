#backend/app/db/session.py
import os
import urllib.parse
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.db.base import Base

logger = logging.getLogger(__name__)

# -------------------------------------------------
# MySQL configuration
# Priority: Environment > Config defaults
# -------------------------------------------------

def build_database_url(dbname: str):
    """
    Builds MySQL DATABASE_URL.
    Database is selected via `dbname`.
    """

    env_password = os.getenv("MYSQL_PASSWORD")

    cfg = {
        "user": os.getenv("MYSQL_USER", "root"),
        "password": "",
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", 3306)),
    }

    password = env_password if env_password else cfg.get("password", "")
    encoded_pw = urllib.parse.quote_plus(password)

    user = cfg["user"]
    host = cfg["host"]
    port = cfg["port"]

    return f"mysql+pymysql://{user}:{encoded_pw}@{host}:{port}/{dbname}"


# -------------------------------------------------
# Primary DB: intradaytrading
# -------------------------------------------------

INTRADAY_DB_NAME = os.getenv("MYSQL_DB", "intradaytrading")
DATABASE_URL = build_database_url(INTRADAY_DB_NAME)

logger.debug(
    "[DB][INIT] Initializing primary DB engine for database=%s",
    INTRADAY_DB_NAME,
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# -------------------------------------------------
# Secondary DB: nifty (market data)
# -------------------------------------------------

NIFTY_DB_NAME = os.getenv("MYSQL_NIFTY_DB", "nifty")
NIFTY_DATABASE_URL = build_database_url(NIFTY_DB_NAME)

logger.debug(
    "[DB][INIT] Initializing NIFTY DB engine for database=%s",
    NIFTY_DB_NAME,
)

engine_nifty = create_engine(
    NIFTY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
)

SessionNifty = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_nifty,
)


# -------------------------------------------------
# FastAPI dependencies
# -------------------------------------------------

def get_db():
    """
    Primary trading engine DB (intradaytrading)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_nifty_db():
    """
    Market data DB (nifty)
    """
    db = SessionNifty()
    try:
        yield db
    finally:
        db.close()