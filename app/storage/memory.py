from app.models.user import User
from .base import BaseStorage


class MemoryStorage(BaseStorage):

    def __init__(self):
        self.storage = dict({"users": []})

    def add_user(self, user: User):
        if len(list(u for u in self.storage["users"] if u.name==user.name and u.ip == user.ip)):
            return
        self.storage["users"].append(user)
    
    def get_user(self,username:str):
        return next((user for user in self.storage["users"] if user.name == username),None)
    
    def get_last_user(self,username:str):
        return next((user for user in reversed(self.storage["users"]) if user.name == username),None)
    
    def get_users(self,username:str):
        return list(user for user in self.storage["users"] if user.name == username)
    
    def get_user_by_ip(self,username:str,ip:str):
        return next((user for user in self.storage["users"] if user.name == username and ip == user.ip),None)
    
    def get_user_diff_ip(self,username:str,ip:str):
        return next((user for user in self.storage["users"] if user.name == username and ip != user.ip),None)
    
    def delete_user(self,username:str,ip:str):
        self.storage["users"] = list(filter(lambda u: u.name!=username and u.ip != ip, self.storage["users"]))
        # self.storage["users"].remove(next(filter(lambda u: u.name!=username and u.ip != ip, self.storage["users"]),None))
        
    def nextCount(self,username:str,ip:str):
        user=next ((u for u in self.storage["users"] if u.name==username and u.ip!=ip),None)
        setattr(user, "count", getattr(user, "count", 0)+1)
