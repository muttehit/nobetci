from app.models.user import User
from .db_base import DBBase
import json
from pathlib import Path
from typing import Any, List


class JsonDb(DBBase):

    data: List[Any]

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.data = self._load()

    def _load(self) -> Any:
        if self.file_path.exists():
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        return []

    def save(self) -> None:
        with open(self.file_path, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)
    
    def add(self,data):
        self.data.append(data)
        self.save()

    def delete(self,condition: callable):
        self.data = list(filter(lambda item: not condition(item), self.data))
        self.save()
    
    def update(self,condition:callable,data):
        filter(lambda item: condition(item), self.data)[0]=data
        self.save()
        
    def get(self,condition:callable):
        return next(filter(lambda item: condition(item), self.data),None)
    
    def get_all(self,condition:callable):
        return list(filter(lambda item: condition(item), self.data))