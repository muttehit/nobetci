"""The base for nobetci storage"""

from abc import ABC, abstractmethod

from app.models.user import User



class BaseStorage(ABC):
    """Base class for nobetci storage"""

    @abstractmethod
    def add_user(self, user: User):
        ""

    @abstractmethod
    def get_user(self,username:str):
        ""
        
    @abstractmethod
    def get_last_user(self,username:str):
        ""
        
    @abstractmethod
    def get_users(self,username:str):
        ""

    @abstractmethod
    def get_user_by_ip(self,username:str,ip:str):
        ""

    @abstractmethod
    def get_user_diff_ip(self,username:str,ip:str):
        ""
        
    @abstractmethod
    def delete_user(self,username:str,ip:str):
        ""
    
    @abstractmethod
    def nextCount(self,username:str,ip:str):
        ""