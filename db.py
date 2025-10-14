# db.py
"""
Multi-engine helper using config.py.
Provides:
  - get_engine(db_key)
  - read_sql(db_key, query, params=None)  -> pandas.DataFrame
  - read_sql_fq(query, params=None)       -> pandas.DataFrame (executes on any engine)
  - execute(db_key, query, params=None)   -> execute statements (use with caution)
"""

import urllib.parse
from sqlalchemy import create_engine, text
import pandas as pd
from typing import Dict
from config import DBS


_engines: Dict[str, object] = {}

def _make_engine(cfg: dict):
    """
    Build SQLAlchemy engine from cfg dict containing:
      host, port, user, password, database, pool_size (optional)
    Password is URL-quoted (for special chars).
    """
    host = cfg.get("host", "localhost")
    port = cfg.get("port", 3306)
    user = cfg.get("user", "root")
    password = cfg.get("password", "")
    database = cfg.get("database", "")
    pool_size = int(cfg.get("pool_size", 5))

    password_enc = urllib.parse.quote_plus(str(password))
    url = f"mysql+pymysql://{user}:{password_enc}@{host}:{port}/{database}?charset=utf8mb4"
    # You can tune pool_pre_ping, pool_recycle, etc. if needed.
    return create_engine(url, pool_size=pool_size, pool_pre_ping=True)

# Create engines for every key provided in config.DBS
for key, cfg in DBS.items():
    try:
        _engines[key] = _make_engine(cfg)
    except Exception as e:
        # Keep failing engine out but don't crash import — user can fix config and retry
        _engines[key] = None
        print(f"[db.py] warning: failed to create engine for '{key}': {e}")

def get_engine(db_key: str):
    if db_key not in _engines:
        raise KeyError(f"Unknown db_key '{db_key}'. Known keys: {list(_engines.keys())}")
    eng = _engines[db_key]
    if eng is None:
        raise RuntimeError(f"Engine for '{db_key}' is not available. Check config.py.")
    return eng

def read_sql(db_key: str, query: str, params: dict = None) -> pd.DataFrame:
    """
    Run a SELECT query against the engine identified by db_key.
    Returns a pandas DataFrame.
    """
    eng = get_engine(db_key)
    with eng.connect() as conn:
        # Use text() to allow bound params
        return pd.read_sql_query(text(query), conn, params=params or {})

def read_sql_fq(query: str, params: dict = None, prefer_db: str = "nifty") -> pd.DataFrame:
    """
    Run a SQL query that may contain fully-qualified table names (db.table).
    Uses the engine for prefer_db to make the connection. That engine's DB user must
    have privileges to read the referenced schemas if they are on the same server.
    """
    eng = get_engine(prefer_db)
    with eng.connect() as conn:
        return pd.read_sql_query(text(query), conn, params=params or {})

def execute(db_key: str, query: str, params: dict = None):
    """
    Execute a non-select statement (INSERT/UPDATE/DDL). Returns ResultProxy.
    Use with caution — this helper is available if needed.
    """
    eng = get_engine(db_key)
    with eng.begin() as conn:
        return conn.execute(text(query), params or {})
