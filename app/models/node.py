from enum import Enum
from pydantic import BaseModel


class Node(BaseModel):
    id: int
    name: str
    address: str
    port: int
    status: str
    message: str | None = None
    
class NodeStatus(str, Enum):
    healthy = "healthy"
    unhealthy = "unhealthy"
    disabled = "disabled"

class AddNode(BaseModel):
    name: str
    address: str
    port: int
    status: str
    message: str | None = None

class UpdateNode(BaseModel):
    name: str
    address: str
    port: int
    status: str
    message: str | None = None