import logging

from fastapi import APIRouter, Body, Query
from fastapi.security import OAuth2PasswordBearer
from app import user_limit_db, storage

from app.db import models
from app.deps import SudoAdminDep
from app.models.user import AddUser, BanUser, UpdateUser, User
from app.nobetnode import nodes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["User"])


@router.get("")
async def get(admin: SudoAdminDep):
    return {"success": True, "data": user_limit_db.get_all(True)}


@router.get("/{username}")
async def get_by_username(username: str, admin: SudoAdminDep):
    user = user_limit_db.get(models.UserLimit.name == username)
    return {"success": user != None, "data": user}


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


@router.post("/{username}/ban")
async def ban(username: str, admin: SudoAdminDep, duration: str = Query(None, description="Ban timeout")):
    for user in storage.get_users(username):
        for node in nodes.keys():
            try:
                await nodes[node].BanUser(user, duration or None)
            except Exception as err:
                logger.error(f'error (node: {node}): ', err)
        storage.delete_user(user.name, user.ip)
    return {"success": True}


@router.post("/{username}/ban/{ip}")
async def ban_by_ip(username: str, ip: str, admin: SudoAdminDep, duration: str = Query(None, description="Ban timeout")):
    for node in nodes.keys():
        try:
            await nodes[node].BanUser(User(name=username, status=None, ip=ip, count=0), duration or None)
        except Exception as err:
            logger.error(f'error (node: {node}): ', err)
    storage.delete_user(username, ip)
    return {"success": True}


@router.post("/{username}/unban/{ip}")
async def unban_by_ip(username: str, ip: str, admin: SudoAdminDep):
    for node in nodes.keys():
        try:
            await nodes[node].UnBanUser(User(name=username, status=None, ip=ip, count=0))
        except Exception as err:
            logger.error(f'error (node: {node}): ', err)
    return {"success": True}


@router.get("/{username}/active_ips")
async def active_ips(username: str, admin: SudoAdminDep):
    userips = list(map(lambda x: x.ip, storage.get_users(username)))

    return {"success": True, "data": userips}


@router.post("/ban/bulk")
async def ban_by_ip_bulk(usernames: list[str], admin: SudoAdminDep, duration: str = Query(None, description="Ban timeout")):
    for username in usernames:
        for user in storage.get_users(username):
            for node in nodes.keys():
                try:
                    await nodes[node].BanUser(user, duration or None)
                except Exception as err:
                    logger.error(f'error (node: {node}): ', err)
            storage.delete_user(user.name, user.ip)
    return {"success": True}


@router.post("/ban/bulk/ip")
async def ban_by_ip_bulk(admin: SudoAdminDep, duration: str = Query(None, description="Ban timeout"), users: list[BanUser] = Body(..., description="List of users to ban by IP")):
    for user in users:
        for node in nodes.keys():
            try:
                await nodes[node].BanUser(User(name=user.name, status=None, ip=user.ip, count=0), duration or None)
            except Exception as err:
                logger.error(f'error (node: {node}): ', err)
        storage.delete_user(user.name, user.ip)
    return {"success": True}


@router.post("/unban/buil/ip")
async def unban_by_ip_bulk(admin: SudoAdminDep, users: list[BanUser] = Body(..., description="List of users to unban by IP")):
    for node in nodes.keys():
        try:
            for user in users:
                await nodes[node].UnBanUser(User(name=user.name, status=None, ip=user.ip, count=0))
        except Exception as err:
            logger.error(f'error (node: {node}): ', err)
    return {"success": True}

