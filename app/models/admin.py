from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


class Token(BaseModel):
    access_token: str
    is_sudo: bool
    token_type: str = "bearer"


class Admin(BaseModel):
    id: int | None = None
    username: str
    is_sudo: bool
