from app import nobetnode
from app.models.node import Node
from app.models.tls import TLS
from app.utils.tls import get_tls_certificate


async def nodes_startup(nodes):
    certificate = get_tls_certificate()
    for node in nodes:
        await nobetnode.operations.add_node(node, TLS(**certificate.__dict__))
