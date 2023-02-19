from flask import Flask, has_request_context, request
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
from flask_pymongo import PyMongo
import logging
import requests
import json
import os

mysqlDB = SQLAlchemy()
logger = logging.getLogger()

def register_extentions(app):
    mysqlDB.init_app(app)

def register_blueprints(app):
    for module_name in (['home']):
        module = import_module(f'apps.{module_name}.routes')
        app.register_blueprint(module.blueprint)

def configure_database(app):
    @app.before_first_request
    def init_database():
        mysqlDB.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        mysqlDB.session.remove()

def configure_logger():
    #getting request level log
    class RequestFormatter(logging.Formatter):
        def format(self, record):
            if has_request_context():
                record.url = request.url
                record.remote_addr = request.remote_addr
            else:
                record.url = None
                record.remote_addr = None
            return super().format(record)

    logFormatter = RequestFormatter(
        '[%(asctime)s] %(levelname)s %(remote_addr)s requested %(url)s in %(module)s: %(message)s'
    )
    # add console handler to the root logger
    consoleHanlder = logging.StreamHandler()
    consoleHanlder.setFormatter(logFormatter)
    logger.addHandler(consoleHanlder)

    # add file handler to the root logger
    fileHandler = logging.FileHandler("apps/logs/applog.log")
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)
    logger.setLevel('INFO')

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extentions(app)
    register_blueprints(app)
    configure_database(app)
    configure_logger()
    return app

