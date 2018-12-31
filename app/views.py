# -*- coding: utf-8 -*-

import datetime
import json
import urllib.request
import urllib.error
import urllib.parse
import requests as httpreq
import base64
import copy
import flask
import os
import math
from flask import Flask, request, url_for, redirect, g, session, flash, \
     abort, render_template, get_flashed_messages, url_for, jsonify, send_from_directory

import flask_restful as restful
from flask_paginate import Pagination

from flask_mail import Message

import flask_login as login
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required

import flask_admin as admin
from flask_admin.contrib import sqla
from flask_admin import helpers, expose

from sqlalchemy import or_
from sqlalchemy.orm import aliased
from sqlalchemy import desc

import uuid, OpenSSL


from app.server import app, api, ma, mail, flask_bcrypt
from app1.models import *
from app.serializers import *
from app.utils import get_user_session_by_userid

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

def output_json(data, code):
    resp = (data, code, {'Content-Type': 'application/json; charset=utf-8'})
    return resp

@app.route('/')
def index():
    currentsession = get_user_session_by_userid()

    if currentsession['login']:
        return redirect(url_for('dashboard'))
    else:
        news = News.query.filter_by(active = 1)
        return render_template('index.html',  currentsession = currentsession, news = news)

@app.route('/notactive')
@app.route('/notactive/')
def notactive():
    app.logger.debug("Start notactive...")
    currentsession = get_user_session_by_userid()
    return render_template('notactive.html',  currentsession = currentsession)

@app.route('/trialexpire')
@app.route('/trialexpire/')
def trialexpire():
    app.logger.debug("Start trialexpire...")
    currentsession = get_user_session_by_userid()
    return render_template('trialexpire.html',  currentsession = currentsession)

@app.route('/forgot')
@app.route('/forgot/')
def forgot():
    currentsession = get_user_session_by_userid()
    return render_template('forgot.html',  currentsession = currentsession)

@app.route('/about')
@app.route('/about/')
def about():
    currentsession = get_user_session_by_userid()
    return render_template('about.html',  currentsession = currentsession)

@app.route('/success')
@app.route('/success/')
def success():
    currentsession = get_user_session_by_userid()
    return render_template('success.html',  currentsession = currentsession)

@app.route('/login', methods=["GET", "POST"])
@app.route('/login/', methods=["GET", "POST"])
def login():
    app.logger.debug("Start login...")
    currentsession = get_user_session_by_userid()
    if request.method == "GET":
        app.logger.debug("Start GET login page...")
        return render_template("login.html", currentsession = currentsession,
                               title = 'Sign In')
    remember_me = False
    data = request.get_json(force=True)
    login = data["username"]
    password = data["password"]
    # registered_user = User.query.filter_by(username=login).first()
    registered_user  = User.query.filter((User.username == data['username']) | (User.email == data['username'])).first()

    if not registered_user:
        resp = {'usererror':1, 'status':409, 'text': 'Username incorrect' }
        return output_json(json.dumps(resp), 200)
    elif not flask_bcrypt.check_password_hash(registered_user.password, password):
        resp = {'passerror':1, 'status':409, 'text': 'Password incorrect' }
        return output_json(json.dumps(resp), 200)
    if not registered_user.active:
        resp = {'activeerror':1, 'status':409, 'text': 'User not active' }
        return output_json(json.dumps(resp), 200)
    else:
        if not registered_user.paidservice:
            now = datetime.datetime.now()
            date_stop_point = registered_user.create_date + datetime.timedelta(days=7)
            if date_stop_point < now:
                resp = {'trialexpire':1, 'status':409, 'text': 'Trial period expire' }
                return output_json(json.dumps(resp), 200)

        session['username'] = registered_user.username
        login_user(registered_user, remember=remember_me)
        registered_user.login_date = datetime.datetime.now()
        db_session.flush()
        db_session.commit()
        resp = {'status':200, 'text': 'Login ok' }
        return output_json(json.dumps(resp), 200)

@app.route('/logout')
@app.route('/logout/')
@login_required
def logout():
    session.pop(current_user.get_name(), None)
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@app.route('/dashboard/')
@login_required
def dashboard():
    app.logger.debug("Start dashboard...")
    currentsession = get_user_session_by_userid()
    return render_template('dashboard.html',  currentsession = currentsession)

@app.route('/contactus')
@app.route('/contactus/')
@login_required
def contactus():
    app.logger.debug("Start contactus...")
    currentsession = get_user_session_by_userid()
    return render_template('contactus.html',  currentsession = currentsession)

@app.route('/changepassword/<path:pathtoapi>',methods=["GET"])
def changepassword(pathtoapi):
    app.logger.debug("Start contactus...")
    currentsession = get_user_session_by_userid()
    passwordcode = pathtoapi
    return render_template('changepassword.html',  currentsession = currentsession, passwordcode = passwordcode)

@app.route('/api/v1/serviceprovider',methods=["GET"])
@app.route('/api/v1/serviceprovider/',methods=["GET"])
def get__serviceprovider():
    app.logger.debug("Start newuser add...")
    currentsession = get_user_session_by_userid()
    try:
        sp = ServiceProvider.query.all()
        schema = ServiceProviderSerializer(many=True)
        resp = schema.dump(sp).data
        resp = {'data':resp}
        return output_json(json.dumps(resp), 200)
    except Exception as e:
        app.logger.error("Error get__serviceprovider %s" % e)
        resp = {"statustype": "error", "message": "Error get serviceprovider.", 'status': 500}
        return output_json(json.dumps(resp), 500)


@app.route('/api/v1/feedback/',methods=["POST"])
@app.route('/api/v1/feedback/',methods=["POST"])
@login_required
def feedback():
    app.logger.debug("Start send feedback...")
    currentsession = get_user_session_by_userid()
    try:
        data = request.get_json(force=True)
        subject = data['subject']
        text = data['description']
        user = currentsession['user']
        subject = "From user %s, %s" %(user.username, subject)
        msg = Message(subject, sender = user.email, recipients = [app.config['ADMINS']])
        msg.body = text
        mail.send(msg)
        resp = {"message": "Send ok.", 'status': 200}
        return output_json(json.dumps(resp), 200)
    except Exception as e:
        app.logger.error("Error send freedback%s" % e)
        resp = {"statustype": "error", "message": "Error send freedback", 'status': 409}
        return output_json(json.dumps(resp), 500)

@app.route('/api/v1/newuser',methods=["POST"])
@app.route('/api/v1/newuser/',methods=["POST"])
def newuser():
    app.logger.debug("Start newuser add...")
    currentsession = get_user_session_by_userid()
    try:
        data = request.get_json(force=True)
        users = User.query.filter_by(username = data['username']).first()
        email = User.query.filter_by(email = data['email']).first()
        resp = {}
        resp['status'] = 200
        if users:
            resp['usererror'] = 1
            resp['status'] = 409
        if email:
            resp['emailerror'] = 1
            resp['status'] = 409

        if resp['status'] == 409:
            return output_json(json.dumps(resp), 200)
        user = User(data['username'], data['password'])
        user.email = data['email']
        user.mobilenumber = data['mobilenumber']
        user.descriptions = data['referfrom']

        serviceprovidername = data['serviceprovidername']
        if (serviceprovidername != ''):
            sp = ServiceProvider()
            sp.name = serviceprovidername
            db_session.add(sp)
            db_session.commit()
            user.serviceprovider = sp
        else:
            sp = ServiceProvider.query.filter_by(serviceprovider_id = int(data['serviceprovider'])).first()
            if sp:
                user.serviceprovider = sp
        user.active = 1
        user.paidservice = 0
        user.create_date = datetime.datetime.now()
        user.modified_date = datetime.datetime.now()
        db_session.add(user)
        db_session.commit()

        resp = {"statustype": "", "message": "User add ok.", 'status': 200}
        return output_json(json.dumps(resp), 200)
    except Exception as e:
        app.logger.error("Error add new user %s" % e)
        resp = {"statustype": "error", "message": "Error add user.", 'status': 409}
        return output_json(json.dumps(resp), 500)


@app.route('/api/v1/getuserdata',methods=["GET"])
@app.route('/api/v1/getuserdata/',methods=["GET"])
@login_required
def getuserdata():
    app.logger.debug("Start getuserdata...")
    currentsession = get_user_session_by_userid()
    user = currentsession['user']
    totaldata = StockWatchlist.query.filter_by(users_id = user.users_id).count()
    data = StockWatchlist.query.filter_by(users_id = user.users_id).all()

    schema = StockWatchlistSerializer(many=True)
    resp = schema.dump(data).data
    resp = {'data':resp, 'total':totaldata}
    return output_json(json.dumps(resp), 200)

@app.route('/api/v1/adddata',methods=["POST"])
@app.route('/api/v1/adddata/',methods=["POST"])
@login_required
def adddata():
    app.logger.debug("Start add data...")
    currentsession = get_user_session_by_userid()
    user = currentsession['user']
    totaldata = StockWatchlist.query.filter_by(users_id = user.users_id).count()
    if (user.paidservice or totaldata < 5) and totaldata < 50:
        try:
            data = request.get_json(force=True)
            userdata = StockWatchlist()
            userdata.users_id = user.users_id
            userdata.symbol = data['symbol']
            userdata.type = data['type']
            userdata.percent = float(data['percent'])
            enabletype = int(data['enabletype'])
            if enabletype == 1:
                enabletype = True
            else:
                enabletype = False

            userdata.enabletype = enabletype
            userdata.create_date = datetime.datetime.now()
            userdata.modified_date = datetime.datetime.now()
            db_session.add(userdata)
            db_session.commit()

            resp = {"statustype": "", "message": "User data add ok.", 'status': 200}
            return output_json(json.dumps(resp), 200)
        except Exception as e:
            db_session.rollback()
            app.logger.error("Error add data %s" % e)
            resp = {"adderror": 1, "message": "Error add data", 'status': 409}
            return output_json(json.dumps(resp), 200)
    else:
        resp = {"trialexpire": 1, "message": "Max add data", 'status': 409}
        if totaldata >= 50:
            resp['trialexpire'] = 2
        return output_json(json.dumps(resp), 200)

@app.route('/api/v1/chdata',methods=["POST"])
@app.route('/api/v1/chdata/',methods=["POST"])
@login_required
def chdata():
    app.logger.debug("Start change data...")
    currentsession = get_user_session_by_userid()
    user = currentsession['user']
    totaldata = StockWatchlist.query.filter_by(users_id = user.users_id).count()
    if user.paidservice or totaldata < 5:
        try:
            data = request.get_json(force=True)
            userdata = StockWatchlist.query.filter_by(id = data['id'], users_id = user.users_id).first()
            userdata.symbol = data['symbol']
            userdata.type = data['type']
            userdata.percent = float(data['percent'])
            enabletype = int(data['enabletype'])
            if enabletype == 1:
                enabletype = True
            else:
                enabletype = False

            userdata.enabletype = enabletype
            userdata.modified_date = datetime.datetime.now()
            db_session.flush()
            db_session.commit()

            resp = {"statustype": "", "message": "User data change ok.", 'status': 200}
            return output_json(json.dumps(resp), 200)
        except Exception as e:
            db_session.rollback()
            app.logger.error("Error add data %s" % e)
            resp = {"changeerror": 1, "message": "Error change data", 'status': 409}
            return output_json(json.dumps(resp), 200)
    else:
        resp = {"trialexpire": 1, "message": "Max add data", 'status': 409}
        return output_json(json.dumps(resp), 200)

@app.route('/api/v1/deldata',methods=["POST"])
@app.route('/api/v1/deldata/',methods=["POST"])
@login_required
def deldata():
    app.logger.debug("Start delete data...")
    currentsession = get_user_session_by_userid()
    user = currentsession['user']
    try:
        data = request.get_json(force=True)
        data = StockWatchlist.query.filter_by(id = data['iddata'], users_id = user.users_id).first()
        db_session.delete(data)
        db_session.commit()
        resp = {"statustype": "", "message": "Delete user data add ok.", 'status': 200}
        return output_json(json.dumps(resp), 200)
    except Exception as e:
        db_session.rollback()
        app.logger.error("Error delete user data %s" % e)
        resp = {"adderror": 1, "message": "Error delete user data", 'status': 409}
        return output_json(json.dumps(resp), 200)

@app.route('/api/v1/forgotpassword',methods=["POST"])
@app.route('/api/v1/forgotpassword/',methods=["POST"])
def forgotpassword():
    app.logger.debug("Start forgotpassword...")
    currentsession = get_user_session_by_userid()
    try:
        data = request.get_json(force=True)
        user = User.query.filter((User.username == data['username']) | (User.email == data['username'])).first()

        if user:
            rpasswd = "".join(str(uuid.UUID(bytes = OpenSSL.rand.bytes(16))).split("-"))

            user.passwordchange = rpasswd
            user.modified_date = datetime.datetime.now()
            db_session.flush()
            db_session.commit()

            subject = 'You stockmarketwaves account '
            text = """
Dear user,

You username: %s

Please click on the following link to visit change password page:
http://www.stockmarketwaves.tk/changepassword/%s

Regards,
The Stockmarketwaves team
""" % (user.username, rpasswd)

            msg = Message(subject, sender = app.config['ADMINS'], recipients = [user.email])
            msg.body = text
            mail.send(msg)

            resp = {"statustype": "", "message": "Get user data ok.", 'status': 200}
            return output_json(json.dumps(resp), 200)
        else:
            resp = {"usernamerror": 1, "message": "Username or email not correct.", 'status': 409}
            return output_json(json.dumps(resp), 200)
    except Exception as e:
        db_session.rollback()
        app.logger.error("Can't get user data %s" % e)
        resp = {"getusererror": 1, "message": "Can't get user data ", 'status': 409}
        return output_json(json.dumps(resp), 200)

@app.route('/api/v1/changepassword',methods=["POST"])
@app.route('/api/v1/changepassword/',methods=["POST"])
def apichangepassword():
    app.logger.debug("Start changepassword...")
    currentsession = get_user_session_by_userid()
    try:
        data = request.get_json(force=True)
        passwordcode = data['passwordcode']
        user = User.query.filter_by(passwordchange = passwordcode).first()
        if user:
            newpasswd = data['password']
            confirmpasswd = data['repassword']
            if newpasswd == confirmpasswd:
                newpasswd = flask_bcrypt.generate_password_hash(newpasswd)
                user.password = newpasswd
                user.passwordchange = ""
                db_session.flush()
                db_session.commit()
                resp = {"message": "Password change", 'status': 200}
                return output_json(json.dumps(resp), 200)

        resp = {"passworderror": 1, "message": "Can't change password ", 'status': 409}
        return output_json(json.dumps(resp), 200)
    except Exception as e:
        db_session.rollback()
        app.logger.error("Can't change user password %s" % e)
        resp = {"passworderror": 1, "message": "Can't change user password", 'status': 409}
        return output_json(json.dumps(resp), 200)


@app.route('/api/v1/getfulllist',methods=["get"])
@app.route('/api/v1/getfulllist/',methods=["get"])
@login_required
def getfulllist():
    app.logger.debug("Start getfulllist...")
    currentsession = get_user_session_by_userid()
    currentuser = currentsession['user']
    if currentuser.username == 'admin':
        outdata = []
        userchema = UserSerializer()
        schema = StockWatchlistSerializer(many=True)
        try:
            sp = ServiceProvider.query.all()
            posfix = {}
            for row in sp:
                if (row.postfix != ''):
                    posfix[row.serviceprovider_id] = row.postfix
                else:
                    posfix[row.serviceprovider_id] = 'Satellink'
            totalusers = User.query.count()
            users = User.query.all()
            for user in users:
                totaluserdata = StockWatchlist.query.filter_by(users_id = user.users_id).count()
                totaldata = StockWatchlist.query.filter_by(users_id = user.users_id)
                userdetail = userchema.dump(user).data
                resp = schema.dump(totaldata).data
                try:
                    postfixs = posfix[user.serviceprovider_id]
                except:
                    postfixs = 'Satellink'
                phone = "%s@%s" %(user.mobilenumber, posfix[user.serviceprovider_id])
                userdata = {'user': user.username,'phone': phone, 'detail': userdetail, 'userdata': resp, 'total': totaluserdata}
                outdata.append(userdata)
            resp = {"totalusers": totalusers, "data": outdata, 'status': 200}
            return output_json(json.dumps(resp), 200)
        except Exception as e:
            app.logger.error("Can't get data list %s" % e)
            resp = {"getlisterror": 1, "message": "Can't get data list ", 'status': 409}
            return output_json(json.dumps(resp), 200)
    else:
        resp = {"getlisterror": 1, "message": "You can't get data list ", 'status': 409}
        return output_json(json.dumps(resp), 200)


@app.route('/api/v1/DF455dDFFG/getfulllist',methods=["get"])
@app.route('/api/v1/DF455dDFFG/getfulllist/',methods=["get"])
def getfulllistn():
    app.logger.debug("Start getfulllistn...")
    if True:
        outdata = []
        userchema = UserSerializer()
        schema = StockWatchlistSerializer(many=True)
        try:
            sp = ServiceProvider.query.all()
            posfix = {}
            for row in sp:
                if (row.postfix != ''):
                    posfix[row.serviceprovider_id] = row.postfix
                else:
                    posfix[row.serviceprovider_id] = 'Satellink'
            totalusers = User.query.count()
            users = User.query.all()
            for user in users:
                totaluserdata = StockWatchlist.query.filter_by(users_id = user.users_id).count()
                totaldata = StockWatchlist.query.filter_by(users_id = user.users_id)
                userdetail = userchema.dump(user).data
                resp = schema.dump(totaldata).data
                try:
                    postfixs = posfix[user.serviceprovider_id]
                except:
                    postfixs = 'Satellink'
                phone = "%s@%s" %(user.mobilenumber, posfix[user.serviceprovider_id])
                userdata = {'user': user.username,'phone': phone, 'detail': userdetail, 'userdata': resp, 'total': totaluserdata}
                outdata.append(userdata)
            resp = {"totalusers": totalusers, "data": outdata, 'status': 200}
            return output_json(json.dumps(resp), 200)
        except Exception as e:
            app.logger.error("Can't get data list %s" % e)
            resp = {"getlisterror": 1, "message": "Can't get data list ", 'status': 409}
            return output_json(json.dumps(resp), 200)
    else:
        resp = {"getlisterror": 1, "message": "You can't get data list ", 'status': 409}
        return output_json(json.dumps(resp), 200)
