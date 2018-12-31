# -*- coding: utf-8 -*-
import os
import sys
import logging
import logging.handlers
import math
import sqlite3
from flask import Flask, g
import flask_restful as restful
from flask_restful import reqparse, Api
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, jsonify
from flask_marshmallow import Marshmallow
from flask_mail  import Mail, Message

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.contrib.fixers import ProxyFix

import logging

basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../')


app = Flask(__name__)
app.debug = True

srvlogfile = 'logs/app.log'
if os.path.isfile(srvlogfile):
    os.remove(srvlogfile)

f = logging.Formatter(fmt='%(levelname)s:%(name)s: %(message)s (%(asctime)s; %(filename)s:%(lineno)d)',
                      datefmt="%Y-%m-%d %H:%M:%S")
handlers = [logging.handlers.RotatingFileHandler(srvlogfile, encoding='utf8', maxBytes=100000, backupCount=1)]

for h in handlers:
    h.setFormatter(f)
    h.setLevel(logging.DEBUG)
    app.logger.addHandler(h)

app.logger.setLevel(logging.INFO)
app.logger.info("start server...")

app.config.from_object('config.ProductionConfig')
db = SQLAlchemy(app)
db.create_all()
api = restful.Api(app)
ma = Marshmallow(app)
mail = Mail(app)
flask_bcrypt = Bcrypt(app)

import app.views
from app.models import *

from app.admin.views import myadmins
app.register_blueprint(myadmins, url_prefix='/admin')

app.wsgi_app = ProxyFix(app.wsgi_app)

@app.after_request
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response
