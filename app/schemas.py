import datetime
import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

class UserCreate(BaseModel):
	model_config = ConfigDict(extra='forbid')  # Strictly forbid extra fields
	
	name: str = Field(min_length=2, max_length=200)
	email: EmailStr
	date_of_birth: datetime.date
	job_title: Optional[str] = Field(default=None, max_length=200)
	password: str = Field(min_length=12, max_length=128)

	@field_validator("password")
	@classmethod
	def password_policy(cls, v: str) -> str:
		has_upper = any(c.isupper() for c in v)
		has_lower = any(c.islower() for c in v)
		has_digit = any(c.isdigit() for c in v)
		has_symbol = any(not c.isalnum() for c in v)
		if not (has_upper and has_lower and has_digit and has_symbol):
			raise ValueError("Password must include upper, lower, digit, and symbol")
		return v

class LoginRequest(BaseModel):
	model_config = ConfigDict(extra='forbid')  # Strictly forbid extra fields
	
	email: EmailStr
	password: str

class UserOut(BaseModel):
	model_config = ConfigDict(from_attributes=True)
	
	id: uuid.UUID
	name: str
	email: EmailStr
	date_of_birth: datetime.date
	job_title: Optional[str]
	role: str

class TokenResponse(BaseModel):
	access_token: str
	token_type: str = "bearer"
	expires_in: int