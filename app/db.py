import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DB_FILENAME

DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///./{DB_FILENAME}"

engine = create_engine(
	DATABASE_URL,
	connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db() -> None:
	from . import models  # noqa: F401
	Base.metadata.create_all(bind=engine)

def get_db() -> Generator:
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()