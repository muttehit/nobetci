from pydantic import BaseModel


class Panel(BaseModel):
    username: str
    password: str
    domain: str
    token: str | None = None