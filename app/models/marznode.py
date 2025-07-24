from enum import Enum
from pydantic import BaseModel


class MarzNode(BaseModel):
    id: int
    name: str
    address: str
    port: int
    status: str
    message: str | None = None