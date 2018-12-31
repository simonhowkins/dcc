# DCC - Digital Command Control command station
# Copyright (C) 2018 Simon Howkins
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Source for this program is published at https://github.com/simonhowkins/dcc

"""Engine model"""
from sqlalchemy import Column
from sqlalchemy.types import Integer, String

from app.models import Base

class Engine(Base):
    __tablename__ = "Engine"

    id = Column(Integer, primary_key=True)
    nickname = Column(String(100))
    addr = Column(Integer)

    maxSpeed = Column(Integer)
    acceleration = Column(Integer)
    braking = Column(Integer)

    def __init__(self, nickname='', addr=0, maxSpeed=28, acceleration=100, braking=100):
        self.nickname = nickname
        self.addr = addr
        self.maxSpeed = maxSpeed
        self.acceleration = acceleration
        self.braking = braking

    def __repr__(self):
        return "Engine[nickname=%s,addr=%s]" % (self.nickname, self.addr)
