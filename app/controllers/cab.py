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

from pyramid_handlers import action

import app.controllers
from app.models.dcc_channel import DccChannel
from app.models.engine import Engine

class CabController(object):

    # The lifetime of these objects is a single HTTP request
    def __init__(self, request):
        self.request = request

    # User has selected an engine to drive, by engine ID
    @action(renderer="app:templates/cab/drive.mako")
    def drive(self):
        id = self.request.params.get("id", None)
        dbSession = app.controllers.settings["DBSession"]
        engine_q = dbSession.query(Engine)
        e = engine_q.get(id)
        return {
            "addr": e.addr,
            "maxSpeed": e.maxSpeed,
        }

    # User is driving engine
    @action(renderer='json')
    def update(self):
        # Find the channel the user is controlling
        addr = self.request.params.get("id", None)
        channel = DccChannel(addr)
        # Update the channel with the user's request, if applicable
        if ("throttle" in self.request.params):
            channel.throttle = int(self.request.params.get("throttle"))
        if ("direction" in self.request.params):
            channel.direction = int(self.request.params.get("direction"))
        # Return the channel status for the ui to display
        return {
            "throttle": channel.throttle,
            "speed": channel.speed,
            "direction": channel.direction,
        }

