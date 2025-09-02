from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated

from app.database.db import get_db
from app.core import auth_service as AuthService, auth_schema as AuthSchemas
from app.services.user_management import user_service as UserService
from app.schemas.user_management import user as UserSchemas
from app.utils.responses import Response

router = APIRouter()
 

@router.post("/token", response_model=AuthSchemas.TokenResponse, status_code=status.HTTP_200_OK)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate user and return JWT token if valid and active.
    """
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        return Response(
            message="Incorrect username or password",
            status_code=status.HTTP_401_UNAUTHORIZED,
            json_data=None,
        )

    if not getattr(user, "is_active", True):
        return Response(
            message="User account is inactive. Please contact support.",
            status_code=status.HTTP_403_FORBIDDEN,
            json_data=None,
        )

    token = AuthService.create_access_token(data={"sub": user.username})
    
    return Response(
        json_data={"access_token": token, "token_type": "bearer"},
        message="Access Token Created Successfully",
        status_code=status.HTTP_200_OK,
    )




@router.post("/swag-token", response_model=AuthSchemas.Token, status_code=status.HTTP_200_OK)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate user and return JWT token if valid and active.
    """
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        return Response(
            message="Incorrect username or password",
            status_code=status.HTTP_401_UNAUTHORIZED,
            json_data=None,
        )

    if not getattr(user, "is_active", True):
        return Response(
            message="User account is inactive. Please contact support.",
            status_code=status.HTTP_403_FORBIDDEN,
            json_data=None,
        )

    token = AuthService.create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
  

@router.get("/verify-token/")
async def verify_token(
    current_user: Annotated[UserSchemas.UserResponse, Depends(AuthService.get_current_user_info)],
    db: Session = Depends(get_db),
):
    """
    Verify the access token and return user data.
    """
    # Optionally add access info here:
    # access = UserService.get_access_details(db, current_user.role_id)

    return Response(
        json_data={"user": current_user},
        message="Token Verified Successfully",
        status_code=status.HTTP_200_OK,
    )
