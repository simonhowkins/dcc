#! /usr/bin/env python

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

def main(global_config, **settings):
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
            DBSession.commit()

    # Init web app
    settings["DBSession"] = DBSession
    config = Configurator(settings=settings)
    config.add_static_view(name='static', path='app:static')
    config.include('pyramid_handlers')
    config.include('pyramid_mako')
    config.include('pyramid_tm')
    controllers.init(config)
    return config.make_wsgi_app()
