import datetime
import json
import urllib.request
import urllib.error
import urllib.parse
import requests as httpreq
import base64

from flask import Flask, request, url_for, redirect, g, session, flash
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from flask_mail import Message

from sqlalchemy import text, or_

from app.server import app, api, ma, mail, flask_bcrypt
from app.models import *

class EmtyClient():
    pass

def get_user_session_by_userid(*kargs):
    currentsession ={}
    try:
        users_id = current_user.users_id
        registered_user = User.query.filter_by(users_id=users_id).first()
        if registered_user:
            currentsession['login'] = True
            currentsession['user'] = registered_user
        else:
            currentsession['login'] = False
            currentsession['user'] = EmtyClient()

    except Exception as e:
        print("Error get_user_session_by_userid:  %s" % e)
        currentsession['login'] = False
        currentsession['user'] = EmtyClient()

    return currentsession
