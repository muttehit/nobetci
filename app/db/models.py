from sqlalchemy import Column, Integer, String

from app.db.base import Base


class UserLimit(Base):
    __tablename__ = "user_limits"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    limit = Column(Integer, nullable=False)

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    address = Column(String(128), nullable=False)
    port = Column(Integer, nullable=False)
    status = Column(String(32), nullable=False)
    message = Column(String(32), nullable=False)

class TLS(Base):
    __tablename__ = "tls"

    id = Column(Integer, primary_key=True)
    cert = Column(String(4096), nullable=False)
    key = Column(String(4096), nullable=False)
