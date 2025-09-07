import time
import uuid
from typing import Optional, Dict
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .db import get_db
from .models import User
from .config import JWT_ALGORITHM, JWT_EXPIRY_SECONDS, JWT_SIGNING_KEY, JWT_VERIFICATION_KEYS, JWT_ISSUER, JWT_AUDIENCE

# Suppress benign warnings from passlib.
# See: https://github.com/pyca/bcrypt/issues/684#issuecomment-1858400267
import logging
logging.getLogger('passlib').setLevel(logging.ERROR)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def hash_password(password: str) -> str:
	return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
	return pwd_context.verify(plain_password, password_hash)


def create_access_token(subject: uuid.UUID, role: str) -> tuple[str, int]:
	now = int(time.time())
	claims = {
		"iss": JWT_ISSUER,
		"sub": str(subject),  # Convert UUID to string for JWT
		"role": role,
		"aud": JWT_AUDIENCE,
		"jti": str(uuid.uuid4()),
		"iat": now,
		"nbf": now,
		"exp": now + JWT_EXPIRY_SECONDS,
	}
	signing_key = JWT_SIGNING_KEY
	token = jwt.encode(claims, signing_key, algorithm=JWT_ALGORITHM)
	return token, JWT_EXPIRY_SECONDS


def verify_access_token(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
	credentials_exception = HTTPException(status_code=401, detail="Invalid token")

	verification_keys = JWT_VERIFICATION_KEYS
	jwt_decoded = None
	
	# Attempt token verification with each key, until one succeeds or we run out of keys.
	for key_id, verification_key in verification_keys.items():
		try:
			jwt_decoded = jwt.decode(token, verification_key, algorithms=[JWT_ALGORITHM], audience=JWT_AUDIENCE)
			break
		except JWTError:
			continue
	
	if jwt_decoded is None:
		raise credentials_exception
	
	try:
		user_id_str = jwt_decoded.get("sub")
		if user_id_str is None:
			raise credentials_exception
		user_id = uuid.UUID(user_id_str)
	except (ValueError, TypeError):
		raise credentials_exception

	user: Optional[User] = db.query(User).filter(User.id == user_id).first()
	if not user:
		raise credentials_exception
	return user


def require_self_or_admin(target_user_id: uuid.UUID, current_user: User) -> None:
	if current_user.role not in ('user', 'admin'):
		raise HTTPException(status_code=403, detail="Forbidden")

    # Non-admins can only access their own data
	if current_user.role == "user" and current_user.id != target_user_id:
		raise HTTPException(status_code=403, detail="Forbidden")


async def add_security_headers(request: Request, call_next):
	response = await call_next(request)

	response.headers.setdefault("X-Content-Type-Options", "nosniff")
	response.headers.setdefault("X-Frame-Options", "DENY")
	response.headers.setdefault("Referrer-Policy", "no-referrer")
	response.headers.setdefault("Cache-Control", "no-store")

    # Avoid CSP header for api documentation routes.
	if request.url.path not in ["/docs", "/redoc", "/openapi.json"]:
		response.headers.setdefault("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'")
		response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
	
	return response