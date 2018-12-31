#! /usr/bin/env python

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

import re

from pyramid.response import Response
from pyramid_handlers import action

import app.controllers
from app.models.engine import Engine
from pyramid.httpexceptions import *

class ShedController(object):
    __autoexpose__ = re.compile("^[^_]")

    # Constructor - a new controller object is created for each request it
    # will handle
    def __init__(self, request):
        # Remember the request that we're handling, and get a DB handle
        self.request = request
        self.dbSession = app.controllers.settings["DBSession"]
        self.engine_q = self.dbSession.query(Engine)

    @action(renderer="app:templates/shed/index.mako")
    def index(self):
        id = self.request.params.get("id", None)
        engines = self.engine_q.all()
        id = int(id) if id != None else engines[0].id if engines else None
        return {
            "engines": engines,
            "id": id,
        }

    def add(self):
        nickname = self.request.params.getone("nickname")
        addr = int("0" + self.request.params.getone("addr"))
        maxSpeed = int(self.request.params.getone("maxSpeed"))
        acceleration = self.request.params.getone("acceleration")
        braking = self.request.params.getone("braking")

        e = Engine(nickname, addr, maxSpeed, acceleration, braking)
        self.dbSession.add(e)
        self.request.tm.commit()

        raise HTTPFound(self.request.route_url("shed", action="index"))

    def save(self):
        id = int(self.request.params.getone("id"))
        e = self.engine_q.get(id)
        e.nickname = self.request.params.getone("nickname")
        e.addr = self.request.params.getone("addr")
        e.maxSpeed = self.request.params.getone("maxSpeed")
        e.acceleration = self.request.params.getone("acceleration")
        e.braking = self.request.params.getone("braking")
        self.request.tm.commit()
        raise HTTPFound(self.request.route_url("shed", action="index", _query={"id": id}))

    def delete(self):
        id = int(self.request.params.getone("id"))
        self.dbSession.delete(self.engine_q.get(id))
        self.request.tm.commit()
        raise HTTPFound(self.request.route_url("shed", action="index"))
        
