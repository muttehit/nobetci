from typing import Generic, Type, TypeVar
from app.db.base import Base, SessionLocal
from app.db.db_base import DBBase
from sqlalchemy.orm import DeclarativeMeta


T = TypeVar("T", bound=DeclarativeMeta)


class DbContext(DBBase, Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model
        self.db = SessionLocal()

    def save(self) -> None:
        ""

    def add(self, data):
        obj = self.model(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, condition: callable):
        instance = self.db.query(self.model).filter(condition).first()
        if instance:
            self.db.delete(instance)
            self.db.commit()
        return instance

    def update(self, condition: callable, data):
        instance = self.db.query(self.model).filter(condition).first()
        if instance:
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            self.db.commit()
            self.db.refresh(instance)
        return instance

    def get(self, condition: callable):
        return self.db.query(self.model).filter(condition).first()

    def get_all(self, condition: callable):
        return self.db.query(self.model).filter(condition).all()
