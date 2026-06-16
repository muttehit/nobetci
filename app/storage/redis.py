import json

from app.db import redis
from app.models.user import User
from .base import BaseStorage


class RedisStorage(BaseStorage):

    def __init__(self):
        self.redis = redis

    def add_user(self, user: User):
        self.redis.set(f'user:{user.name}:ip:{user.ip}', json.dumps({"node":user.node,"inbound":user.inbound,"accepted":user.accepted}), 120)
    
    def get_user(self,username:str):
        keys = list(self.redis.scan_iter(f'user:{username}:ip:*'))
        value = keys and self.redis.exists(keys[0]) and json.loads(self.redis.get(keys[0]))
        return value and User(name=username, ip=keys[0].split(":")[-1], count=0, inbound=value["inbound"], accepted=value["accepted"], node=value["node"])
    
    def get_last_user(self,username:str):
        keys = list(self.redis.scan_iter(f'user:{username}:ip:*'))
        value = keys and self.redis.exists(keys[-1]) and json.loads(self.redis.get(keys[0]))
        return value and User(name=username, ip=keys[-1].split(":")[-1], count=0, inbound=value["inbound"], accepted=value["accepted"], node=value["node"])
    
    def get_users(self,username:str):
        keys = list(self.redis.scan_iter(f'user:{username}:ip:*'))
        return keys and [User(name=username, ip=key.split(":")[-1], count=0) for key in keys]
    
    def get_user_by_ip(self,username:str,ip:str):
        ""
    
    def get_user_diff_ip(self,username:str,ip:str):
        ""
    
    def delete_user(self,username:str,ip:str):
        self.redis.delete(f'user:{username}:ip:{ip}')
        
    def nextCount(self,username:str,ip:str):
        ""
