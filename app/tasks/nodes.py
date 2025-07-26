from app import nobetnode
from app.models.node import Node
from app.models.tls import TLS
from app.utils.tls import get_tls_certificate
from app.db import node_db


async def nodes_startup():
    certificate = get_tls_certificate()
    db_nodes = node_db.get_all(True)
    for db_node in db_nodes:
        await nobetnode.operations.add_node(db_node, TLS(**certificate.__dict__))