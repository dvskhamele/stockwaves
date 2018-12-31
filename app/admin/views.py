# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

from flask import Flask, Blueprint, request, render_template, make_response, jsonify, url_for, redirect, \
     abort, get_flashed_messages, send_from_directory, g, session
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from app.server import app, db, api, ma, mail, flask_bcrypt
from app.models import db_session, User, News, ServiceProvider, StockWatchlist, init_db, drop_db
import json
import datetime
import math
import urllib.parse
import flask_restful as restful

#import flask_admin as admin

import flask_admin as admin
from flask_admin import Admin, helpers, expose
from flask_admin.base import MenuLink
from flask_admin.contrib.sqlamodel import ModelView
from flask_admin.contrib import sqla
#from flask_admin import helpers, expose

from sqlalchemy import or_
from sqlalchemy.sql import compiler
from app.utils import get_user_session_by_userid

myadmins = Blueprint("admins",__name__,template_folder='templates/admin')

def output_json(data, code):
    resp = (data, code, {'Content-Type': 'application/json; charset=utf-8'})
    return resp


class BaseModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated()

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

class AppAdminIndexView(admin.AdminIndexView):
    @expose('/')
    def index(self):
        currentsession= get_user_session_by_userid()
        if (not current_user.is_authenticated()) or (currentsession['user'].username != 'admin'):
            return redirect(url_for('.login_view'))
        user_list_url = url_for('.logout_view')
        #return self.render('index.html', user_list_url=user_list_url)
        return super(AppAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        currentsession= get_user_session_by_userid()
        if request.method == "GET":
            app.logger.error('login user...')
            return render_template("admin/login_admin.html", currentsession = currentsession,
                                   title = 'Sign In')

        remember_me = False
        data = request.get_json(force=True)
        login = data["username"]
        password = data["password"]
        if login != 'admin':
            return redirect(url_for('login'))

        registered_user = User.query.filter_by(username=login).first()
        if not registered_user:
            return redirect(url_for('login'))

        session['username'] = login
        login_user(registered_user, remember=remember_me)

        if current_user.is_authenticated():
            return redirect(url_for('.index'))

        return super(AppAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        session.pop(current_user.get_name(), None)
        logout_user()
        return redirect(url_for('.index'))

class AppUserAdmin(BaseModelView):
    form_columns = ('username', 'email', 'mobilenumber', 'descriptions', 'serviceprovider', 'stockwatchlist', 'active', 'paidservice', 'amount', 'last_payment_date', 'create_date', 'modified_date', 'login_date')

    excluded_list_columns = ('password','create_date', 'modified_date', 'login_date', 'passwordchange')
    column_searchable_list = ('username', 'email')

admin = Admin(app, 'API ADMIN', index_view=AppAdminIndexView(), template_mode='bootstrap3')
admin.add_view(AppUserAdmin(User, db_session))
admin.add_view(BaseModelView(News, db_session))
admin.add_view(BaseModelView(StockWatchlist, db_session))
admin.add_view(BaseModelView(ServiceProvider, db_session))
admin.add_link(MenuLink(name='Get all data', category='Menu', url='/api/v1/getfulllist/'))
admin.add_link(MenuLink(name='Generate new Db', category='Menu', url='/admin/generate/'))
admin.add_link(MenuLink(name='Logout', category='Menu', url='/admin/logout/'))

@myadmins.route("/generate/",methods=["GET"])
def generate_db():
    app.logger.info("Start make db")
    currentsession= get_user_session_by_userid()
    serviceprovider = ['3 River Wireless', 'ACS Wireless', 'Alltel', 'AT&T', 'Bell Canada', 'Bell Canada', 'Bell Mobility (Canada)', 'Bell Mobility', 'Blue Sky Frog', 'Bluegrass Cellular', 'Boost Mobile', 'BPL Mobile', 'Carolina West Wireless', 'Cellular One', 'Cellular South', 'Centennial Wireless', 'CenturyTel', 'Cingular (Now AT&T)', 'Clearnet', 'Comcast', 'Corr Wireless Communications', 'Dobson', 'Edge Wireless', 'Fido', 'Golden Telecom', 'Helio', 'Houston Cellular', 'Idea Cellular', 'Illinois Valley Cellular', 'Inland Cellular Telephone', 'MCI', 'Metrocall', 'Metrocall 2-way', 'Metro PCS', 'Microcell', 'Midwest Wireless', 'Mobilcomm', 'MTS', 'Nextel', 'OnlineBeep', 'PCS One', "President's Choice", 'Public Service Cellular', 'Qwest', 'Rogers AT&T Wireless', 'Rogers Canada', 'Satellink', 'Southwestern Bell', 'Sprint', 'Sumcom', 'Surewest Communicaitons', 'T-Mobile', 'Telus', 'Tracfone', 'Triton', 'Unicel', 'US Cellular', 'Solo Mobile', 'Sprint', 'Sumcom', 'Surewest Communicaitons', 'T-Mobile', 'Telus', 'Triton', 'Unicel', 'US Cellular', 'US West', 'Verizon', 'Virgin Mobile', 'Virgin Mobile Canada', 'West Central Wireless', 'Western Wireless']
    db_session.close()
    drop_db()
    init_db()

    user = User('admin', '1')
    user.email = 'admin@localhost'
    user.mobilenumber = '800 000 0000'
    user.referfrom = 'admin'
    user.active = 1
    user.paidservice = 1
    user.create_date = datetime.datetime.now()
    user.modified_date = datetime.datetime.now()
    db_session.add(user)
    db_session.commit()


    sps = {}
    for row in serviceprovider:
        if row not in sps:
            sps[row] = 1
            sp = ServiceProvider()
            sp.name = row
            try:
                db_session.add(sp)
                db_session.commit()
            except:
                db_session.rollback()


    return output_json("status:ok", 200)
