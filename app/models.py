import datetime as dt
import uuid
from sqlalchemy import Column, String, Date, DateTime, TypeDecorator
from sqlalchemy.sql import func
from .db import Base

class UUIDString(TypeDecorator):
	"""UUID type that stores as string in SQLite but works with uuid.UUID objects in Python."""
	impl = String(36)
	cache_ok = True

	def process_bind_param(self, value, dialect):
		return str(value)

	def process_result_value(self, value, dialect):
		return uuid.UUID(value)

class User(Base):
	__tablename__ = "users"

	id = Column(UUIDString(), primary_key=True, default=uuid.uuid4, index=True)
	name = Column(String(200), nullable=False)
	email = Column(String(255), unique=True, index=True, nullable=False)
	date_of_birth = Column(Date, nullable=False)
	job_title = Column(String(200), nullable=True)
	password_hash = Column(String(255), nullable=False)
	role = Column(String(50), nullable=False, default="user")

	created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
	updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
	last_login_at = Column(DateTime(timezone=True), nullable=True)

	def __repr__(self) -> str:
		return f"<User id={self.id} email={self.email} role={self.role}>"