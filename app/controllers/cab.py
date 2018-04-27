#! /usr/bin/env python

from pyramid_handlers import action

class CabController(object):

    def __init__(self, request):
        self.request = request

    @action(renderer="app:templates/cab/drive.mako")
    def drive(self):
        id = self.request.params.get("id", None)
        return {
            "addr": id,
        }

