import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..schemas import UserOut
from ..security import verify_access_token, require_self_or_admin

router = APIRouter(
    prefix="/users",
    tags=["User Management"],
    responses={404: {"description": "User not found"}},
)

@router.get(
    "/{user_id}", 
    response_model=UserOut,
    summary="Get user details",
    description="Retrieve user information by ID. Users can only access their own data unless they are an admin.",
    response_description="User details retrieved successfully",
    responses={
        403: {
            "description": "Forbidden - User can only access their own data unless they are an admin",
            "content": {
                "application/json": {
                    "example": {"detail": "Forbidden"}
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        }
    }
)
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(verify_access_token)):
	require_self_or_admin(user_id, current_user)
	user = db.query(User).filter(User.id == user_id).first()
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	return user