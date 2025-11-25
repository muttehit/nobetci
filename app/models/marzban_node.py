from pydantic import BaseModel


class MarzbanNode(BaseModel):
    id: int
    name: str
    address: str
    port: int
    status: str
    message: str | None = None