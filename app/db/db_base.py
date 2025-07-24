"""The base for nobetci storage"""

from abc import ABC, abstractmethod

from app.models.user import User



class DBBase(ABC):
    """Base class for nobetci storage"""

    @abstractmethod
    def save(self) -> None:
        ""
        
    @abstractmethod
    def add(self,data):
        ""

    @abstractmethod
    def delete(self,condition: callable):
        ""
    
    @abstractmethod
    def update(self,condition:callable,data):
        ""
        
    @abstractmethod
    def get(self,condition:callable):
        ""
        
    @abstractmethod
    def get_all(self,condition:callable):
        ""