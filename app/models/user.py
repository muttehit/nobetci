from typing import TYPE_CHECKING

from pydantic import BaseModel
from enum import Enum


class UserStatus(Enum):
    """
    Enum representing the type of UserStatus.

    Attributes:
        ACTIVE (str)
        DISABLE (str)
    """

    ACTIVE = "ACTIVE"
    DISABLE = "DISABLE"


class User(BaseModel):
    name: str
    status: UserStatus | None = None
    inbound: str | None = None
    accepted: str | None = None
    ip: str
    count: int


class AddUser(BaseModel):
    name: str
    limit: int


class UpdateUser(BaseModel):
    limit: int
