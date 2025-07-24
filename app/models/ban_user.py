from typing import TYPE_CHECKING

from pydantic import BaseModel

class BanUser(BaseModel):
    ip: str
    banDuration:int
