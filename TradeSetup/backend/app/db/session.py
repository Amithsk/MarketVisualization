import os
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.db.base import Base

# -------------------------------------------------
# MySQL configuration
# Priority: Environment > Config defaults
# -------------------------------------------------

def build_database_url():
    """
    Builds MySQL DATABASE_URL.
    Schema (database) is selected via `dbname`.
    """

    # ---- Password priority ----
    env_password = os.getenv("MYSQL_PASSWORD")

    # You can later replace this cfg with:
    # - config file
    # - secrets manager
    cfg = {
        "user": os.getenv("MYSQL_USER", "root"),
        "password": "",
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", 3306)),
        "db": os.getenv("MYSQL_DB", "intradaytrading"),
    }

    password = env_password if env_password else cfg.get("password", "")
    encoded_pw = urllib.parse.quote_plus(password)

    user = cfg["user"]
    host = cfg["host"]
    port = cfg["port"]
    dbname = cfg["db"]   # 🔴 THIS IS THE SCHEMA / DATABASE NAME

    return f"mysql+pymysql://{user}:{encoded_pw}@{host}:{port}/{dbname}"


DATABASE_URL = build_database_url()

# -------------------------------------------------
# SQLAlchemy engine & session
# -------------------------------------------------

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
# FastAPI dependency
# -------------------------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()