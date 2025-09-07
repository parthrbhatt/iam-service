import datetime as dt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..schemas import UserCreate, LoginRequest, TokenResponse, UserOut
from ..security import hash_password, verify_password, create_access_token

router = APIRouter(
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)

@router.post(
    "/users", 
    response_model=UserOut, 
    status_code=201,
    summary="Register a new user",
    description="Create a new user account with self-registration. Password must meet security requirements.",
    response_description="User account created successfully"
)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
	existing = db.query(User).filter(User.email == payload.email).first()
	if existing:
		# IMPORTANT: This makes the service vulnerable to enumeration attacks.
		# Ideally, the service should have various security controls like the ones listed below:
		# - WAF to enforce rate limiting and blocking of suspicious requests.
		# - Email verification.
		# - The service can return a generic message instead of "User already exists"
		# It is implemented this way for simplicity.
		raise HTTPException(status_code=409, detail="User already exists")
	password_hash = hash_password(payload.password)
	user = User(
		name=payload.name.strip(),
		email=str(payload.email).lower(),
		date_of_birth=payload.date_of_birth,
		job_title=payload.job_title.strip() if payload.job_title else None,
		password_hash=password_hash,
		role="user", # default role for new users
	)
	db.add(user)
	db.commit()
	db.refresh(user)
	return user

@router.post(
    "/login", 
    response_model=TokenResponse,
    summary="Authenticate user",
    description="Authenticate using email and password to obtain a JWT access token.",
    response_description="Authentication successful, returns access token"
)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
	user = db.query(User).filter(User.email == str(payload.email).lower()).first()
	if not user or not verify_password(payload.password, user.password_hash):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
	user.last_login_at = dt.datetime.utcnow()
	db.add(user)
	db.commit()
	token, expires_in = create_access_token(subject=user.id, role=user.role)
	return TokenResponse(access_token=token, expires_in=expires_in)