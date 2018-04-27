"""Engine model"""
from sqlalchemy import Column
from sqlalchemy.types import Integer, String

from app.models import Base

class Engine(Base):
    __tablename__ = "Engine"

    id = Column(Integer, primary_key=True)
    nickname = Column(String(100))
    addr = Column(Integer)

    def __init__(self, nickname='', addr=0):
        self.nickname = nickname
        self.addr = addr

    def __repr__(self):
        return "Engine[nickname=%s,addr=%s]" % (self.nickname, self.addr)
