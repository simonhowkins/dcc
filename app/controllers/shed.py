#! /usr/bin/env python

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
        addr = int("0" + self.request.params.getone("addr")[0])

        e = Engine(nickname, addr)
        self.dbSession.add(e)
        self.request.tm.commit()

        raise HTTPFound(self.request.route_url("shed", action="index"))

    def save(self):
        id = int(self.request.params.getone("id"))
        e = self.engine_q.get(id)
        e.nickname = self.request.params.getone("nickname")
        e.addr = self.request.params.getone("addr")
        self.request.tm.commit()
        raise HTTPFound(self.request.route_url("shed", action="index", _query={"id": id}))

    def delete(self):
        id = int(self.request.params.getone("id"))
        self.dbSession.delete(self.engine_q.get(id))
        self.request.tm.commit()
        raise HTTPFound(self.request.route_url("shed", action="index"))
        
