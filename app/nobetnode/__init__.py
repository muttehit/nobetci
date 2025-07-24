"""stores nodes and provides entities to communicate with the nodes"""

from typing import Dict

from . import operations
from .base import NobetNodeBase
from .grpclib import NobetNodeGRPCLIB

nodes: Dict[int, NobetNodeBase] = {}


__all__ = [
    "nodes",
    "operations",
    "NobetNodeGRPCLIB",
    "NobetNodeBase",
]