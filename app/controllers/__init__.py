#! /usr/bin/env python

settings = None

def init(config):
    config.add_handler('shed', '/shed/{action}', handler="app.controllers.shed.ShedController")
    config.add_handler('cab', '/cab/{action}', handler="app.controllers.cab.CabController")

    # Store an accessible reference to the app settings
    global settings
    settings = config.get_settings()

