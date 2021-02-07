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

import os
import os.path
import transaction

from sqlalchemy import engine_from_config
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from zope.sqlalchemy import ZopeTransactionExtension

from pyramid.config import Configurator
from pyramid.response import Response

import app.controllers
from app.models import Base
from app.models.engine import Engine
import app.services.dcclib
import app.services.memlib as mem
import app.services.gpiolib

def main(global_config, **settings):
    app.services.dcclib.unit_test()
    # Init hardware (GPIOs, clocks, PWM, DMA)

    # Init database
    needToCreateExampleEngine = not os.path.exists(settings['databaseFile'])
    dbEngine = engine_from_config(settings, 'sqlalchemy.')
    DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
    DBSession.configure(bind=dbEngine)
    Base.metadata.create_all(dbEngine)
    if needToCreateExampleEngine:
        print("No Engine database found - creating sample Engine...")
        with transaction.manager:
            model = Engine(addr=3, nickname='Boxfresh Loco')
            DBSession.add(model)
            transaction.commit()

    # Init web app
    settings["DBSession"] = DBSession
    config = Configurator(settings=settings)
    config.add_static_view(name='static', path='app:static')
    config.include('pyramid_handlers')
    config.include('pyramid_mako')
    config.include('pyramid_tm')
    controllers.init(config)
    return config.make_wsgi_app()
