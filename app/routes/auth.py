from functools import wraps
import logging

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from app.config import API_PASSWORD, API_USERNAME
from app.deps import AdminDep
from app.utils.auth import create_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not (form_data.username == API_USERNAME and form_data.password == API_PASSWORD):
        raise HTTPException(
            status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(API_USERNAME, True)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/protected")
async def protected(admin: AdminDep):
    return {"message": f"Hello, {admin.username}!"}
