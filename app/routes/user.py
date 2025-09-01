import logging

from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer
from app import user_limit_db

from app.db import models
from app.deps import SudoAdminDep
from app.models.user import AddUser, UpdateUser, User
from app.nobetnode import nodes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["User"])


@router.get("")
async def get(admin: SudoAdminDep):
    return {"success": True, "user": user_limit_db.get_all(True)}


@router.get("/{username}")
async def get_by_username(username: str, admin: SudoAdminDep):
    user = user_limit_db.get(models.UserLimit.name == username)
    return {"success": user != None, "user": user}


@router.delete("/{username}")
async def delete(username: str, admin: SudoAdminDep):
    user_limit_db.delete(models.UserLimit.name == username)

    return {"success": True}


@router.post("")
async def add_user(new_user: AddUser, admin: SudoAdminDep):
    if user_limit_db.get(models.UserLimit.name == new_user.name):
        return {"success": True, "message": "User exists"}

    user_limit_db.add({
        "name": new_user.name,
        "limit": new_user.limit
    })

    logger.info("New user `%s` added with `%i` limit",
                new_user.name, new_user.limit)
    return {"success": True}


@router.put("/{username}")
async def add_user(username: str, update_user: UpdateUser, admin: SudoAdminDep):
    user_limit_db.update(models.UserLimit.name == username, {
        "limit": update_user.limit
    })

    logger.info("User `%s` updated with `%i` limit",
                username, update_user.limit)
    return {"success": True}


@router.post("/{username}/unban/{ip}")
async def unbanByIp(username: str, ip: str, admin: SudoAdminDep):
    for node in nodes.keys():
        try:
            await nodes[node].UnBanUser(User(name=username, status=None, ip=ip, count=0))
        except Exception as err:
            logger.error(f'error (node: {node}): ', err)
    return {"success": True}
