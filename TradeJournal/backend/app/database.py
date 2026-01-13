from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import urllib


password = os.getenv('MYSQL_PASSWORD')
encoded_pw = urllib.parse.quote_plus(password)  # Properly escape special characters
DATABASE_URL = f"mysql+pymysql://root:{encoded_pw}@localhost/intradaytrading"


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()
