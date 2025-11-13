from pydantic import BaseModel


class RebeccaNode(BaseModel):
    id: int
    name: str
    address: str
    port: int
    nobetci_port: int | None = None
    status: str
    message: str | None = None
