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
from app.models.dcc_channel import DccChannel

class CabController(object):

    def __init__(self, request):
        self.request = request

    @action(renderer="app:templates/cab/drive.mako")
    def drive(self):
        id = self.request.params.get("id", None)
        return {
            "addr": id,
        }

    @action(renderer='json')
    def update(self):
        channel = DccChannel(self.request.params.get("id"))
        channel.throttle = int(self.request.params.get("throttle"))
        channel.direction = int(self.request.params.get("direction"))
        return {
            "speed": channel.speed,
            "direction": channel.direction,
        }

