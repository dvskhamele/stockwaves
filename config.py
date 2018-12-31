# -*- coding: utf-8 -*-

import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DIRECTORY_SCRIPT = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,DIRECTORY_SCRIPT+"/..")

class Config(object):
    DEBUG = False
    CSRF_ENABLED = True
    WTF_CSRF_ENABLED = False
    THREADS_PER_PAGE = 2
    CSRF_SESSION_KEY = "JDASDmkasdiEE3asd2wSDa3"
    WTF_CSRF_SECRET_KEY = 'XsadassacEExcaesdADASss221acf'
    SECRET_KEY = 'xv3gavkxc04n3mzx7oksEE6q'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# --------------------- DB SERVER ------------------------------------------------------------------------------------
    LOGO_URL = '/static/img/logos'

# -------------------- Email server ---------------------------------------------------------------------------------
    MAIL_ENABLE = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
#    MAIL_USE_TLS = True
    MAIL_USE_SSL = True
    MAIL_USERNAME = "stockmarketwaves@gmail.com"
    MAIL_PASSWORD = "xuxbrqxydzjuvtmy"
#    MAIL_USERNAME = "stockmarketwaverx@gmail.com"
#    MAIL_PASSWORD = "kezmslrbqtinwlxw"

    # administrator list
    ADMINS = MAIL_USERNAME

class ProductionConfig(Config):
    DEBUG = False
    SANDBOX = False
class DevelopConfig(Config):
    DEBUG = True
    SANDBOX = True






