from pydantic import BaseModel


class TLS(BaseModel):
    key: str
    cert: str