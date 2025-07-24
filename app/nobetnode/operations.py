import asyncio
from collections import defaultdict
from typing import TYPE_CHECKING

from app import nobetnode
from .grpclib import NobetNodeGRPCLIB
from ..models.user import User


async def remove_node(node_id: int):
    if node_id in nobetnode.nodes:
        await nobetnode.nodes[node_id].stop()
        del nobetnode.nodes[node_id]


async def add_node(db_node, certificate):
    await remove_node(db_node.id)
    node = NobetNodeGRPCLIB(
        db_node,
        certificate.key,
        certificate.cert,
        # usage_coefficient=db_node.usage_coefficient,
    )
    nobetnode.nodes[db_node.id] = node


__all__ = ["update_user", "add_node", "remove_node"]