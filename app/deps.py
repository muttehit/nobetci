from typing import Annotated
from fastapi import Depends, HTTPException, status

from app.config import API_USERNAME
from app.models.admin import Admin
from app.utils.auth import get_admin_payload

from app.models.admin import oauth2_scheme


def get_admin(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = get_admin_payload(token)

    if not payload:
        return

    dbadmin = Admin(id=None, username=API_USERNAME, is_sudo=True)
    if not dbadmin:
        return

    if not dbadmin.is_sudo:
        return

    return Admin.model_validate(dbadmin)


def get_current_admin(admin: Annotated[Admin, Depends(get_admin)]):
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return admin


def sudo_admin(admin: Annotated[Admin, Depends(get_current_admin)]):
    if not admin.is_sudo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied",
        )
    return admin


AdminDep = Annotated[Admin, Depends(get_current_admin)]
SudoAdminDep = Annotated[Admin, Depends(sudo_admin)]
