# config.py
# Simple centralized DB configuration (no .env). Edit this file to match your environment.
# Use the same credentials for each DB if that's your setup, or provide per-db credentials.

from typing import Dict
import os
import urllib.parse

mysqlpassword = os.getenv('MYSQL_PASSWORD')

# Example 1: same host / user / password for all DBs (most common local setup)
DEFAULT = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password":mysqlpassword ,  # replace with your local password
    "pool_size": 5,
}

# Logical DB entries. Keys used by db.py / queries.py: 'nifty', 'etf', 'intraday'
DBS: Dict[str, dict] = {
    "nifty": {
        **DEFAULT,
        "database": "nifty",
    },
    "etf": {
        **DEFAULT,
        "database": "etf",
    },
    "intraday": {
        **DEFAULT,
        "database": "intradaytrading",
    },
}

# --- Optional: override a single DB with different host/user/password --
# Example (uncomment and edit if needed):
# DBS["etf"] = {
#     "host": "etf-db-host",
#     "port": 3306,
#     "user": "etf_user",
#     "password": "etf_password",
#     "database": "etf",
#     "pool_size": 3,
# }
