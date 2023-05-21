from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# DB_URL = f"mysql://msuser" \
#          f":mspass" \
#          f"@localhost" \
#          f":3306" \
#          f"/equipment"

DB_URL = f"mysql://{os.getenv('MYSQL_USER')}" \
         f":{os.getenv('MYSQL_PASS')}" \
         f"@{os.getenv('MYSQL_HOST')}" \
         f":{os.getenv('MYSQL_PORT')}" \
         f"/{os.getenv('MYSQL_DB')}"

engine = create_engine(
    DB_URL,
    echo=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class DBContext:
    def __init__(self):
        self.db = SessionLocal()

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()


def get_db():
    with DBContext() as db:
        yield db


def setup_database():
    Base.metadata.create_all(engine)
