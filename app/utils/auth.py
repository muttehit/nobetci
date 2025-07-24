from datetime import datetime, timedelta
from typing import Union

from jose import jwt

from app.config import ALGORITHM, SECRET_KEY,ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(username: str, is_sudo=False) -> str:
    if ACCESS_TOKEN_EXPIRE_MINUTES > 0:
        expire = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        data = {
            "sub": username,
            "access": "sudo" if is_sudo else "admin",
            "iat": datetime.utcnow(),
            "exp": expire
        }
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_admin_payload(token: str) -> Union[dict, None]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        return

    username: str = payload.get("sub")
    access: str = payload.get("access")
    if not username or access not in ("admin", "sudo"):
        return
    try:
        created_at = datetime.utcfromtimestamp(payload["iat"])
    except KeyError:
        created_at = None

    return {
        "username": username,
        "is_sudo": access == "sudo",
        "created_at": created_at,
    }
