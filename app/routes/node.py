import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.db import models, node_db, tls_db
from jose import jwt

from app.config import ALGORITHM, API_USERNAME, SECRET_KEY
from app.deps import SudoAdminDep
from app.models.node import AddNode, Node
from app.models.tls import TLS
from app.nobetnode import operations
from app.utils.tls import get_tls_certificate


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/nodes", tags=["Node"])


@router.get("")
async def get(admin: SudoAdminDep):
    return {"success": True, "data": node_db.get_all(True)}


@router.get("/settings")
async def update_node(admin: SudoAdminDep):
    tls = tls_db.get(True)

    return {"success": True, "settings": {"certificate": tls.cert}}


@router.post("")
async def add_node(new_node: AddNode, admin: SudoAdminDep):
    node = node_db.add({
        "name": new_node.name,
        "address": new_node.address,
        "port": new_node.port,
        "status": new_node.status,
        "message": new_node.message
    })

    certificate = get_tls_certificate()

    await operations.add_node(node, TLS(**certificate.__dict__))

    logger.info("Node `%s` added with `%s` address",
                new_node.name, new_node.address)
    return {"success": True}


@router.get("/{id}")
async def get_by_id(id: int, admin: SudoAdminDep):
    return {"success": True, "data": node_db.get(models.Node.id == id)}


@router.delete("/{id}")
async def delete(id: int, admin: SudoAdminDep):
    node_db.delete(models.Node.id == id)

    return {"success": True}


@router.put("/{id}")
async def update_node(id: int, new_node: AddNode, admin: SudoAdminDep):
    node_db.update(models.Node.id == id, {
        "name": new_node.name,
        "address": new_node.address,
        "port": new_node.port,
        "status": new_node.status,
        "message": new_node.message
    })

    logger.info("Node `%s` updated with `%s` address",
                new_node.name, new_node.address)
    return {"success": True}
