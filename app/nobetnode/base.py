from abc import ABC, abstractmethod

from app.models.user import User


class NobetNodeBase(ABC):

    @abstractmethod
    async def BanUser(self, user: User):
        pass