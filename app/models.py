# -*- coding: utf-8 -*-
import codecs
from flask import g, url_for
from flask_login import UserMixin
from wtforms.validators import Email
import uuid
import OpenSSL

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from app.server import app, api, ma, mail, flask_bcrypt
# from app.database import Base

#engine = create_engine('sqlite:////var/www/stockmarketwaves/database.db', convert_unicode=True, echo=True)

engine = create_engine('sqlite:////var/www/stockmarketwaves/database.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import app.models
    Base.metadata.create_all(bind=engine)
    db.create_all()

    # Create a test user
    new_user = User('a@a.com', 'aaaaaaaa')
    new_user.display_name = 'Nathan'
    db.session.add(new_user)

    new_user.datetime_subscription_valid_until = datetime.datetime(2019, 1, 1)
    db.session.commit()



    

def drop_db():
    Base.metadata.drop_all(bind=engine)

class News(Base):
    __tablename__ = 'web_news'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable = True)
    url  = Column(String(255), nullable = True)
    body = Column(Text, nullable = True)
    active = Column(Boolean, nullable=True)
    create_date = Column(DateTime,  nullable = True)
    modified_date = Column(DateTime, nullable = True)

    def get_name(self):
        return self.name

    def __repr__(self):
        return self.name

class ServiceProvider(Base):
    __tablename__ = 'web_serviceprovider'

    serviceprovider_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(65), unique=True, nullable = False)
    postfix = Column(String(65), nullable = True)

    def get_name(self):
        return self.name

    def __repr__(self):
        return self.name

class User(Base, UserMixin):
    __tablename__ = 'web_users'

    users_id = Column(Integer, primary_key=True, autoincrement=True)
    serviceprovider_id = Column(Integer, ForeignKey('web_serviceprovider.serviceprovider_id'), nullable = True)
    username = Column(String(65), unique=True, nullable = False)
    password = Column(String(100), nullable = False)
    email = Column(String(100), unique=True, nullable=False, info={'validators': Email()})
    mobilenumber = Column(String(100), nullable = True)
    descriptions = Column(String(255), nullable = True)
    active = Column(Boolean, nullable=True)
    paidservice = Column(Boolean, nullable=True)
    amount = Column(Float, nullable = True)
    last_payment_date = Column(DateTime,  nullable = True)
    passwordchange  = Column(String(120), nullable = True)
    create_date = Column(DateTime,  nullable = True)
    modified_date = Column(DateTime, nullable = True)
    login_date = Column(DateTime, nullable = True)

    serviceprovider = relationship("ServiceProvider", foreign_keys=[serviceprovider_id], backref=backref("user"))

    def __init__(self, email, password):
        self.username = email
        self.password = flask_bcrypt.generate_password_hash(password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.users_id)

    def get_name(self):
        return self.username

    def __repr__(self):
        return self.username

class StockWatchlist(Base):
    __tablename__ = 'web_stockwatchlist'
    id = Column(Integer, primary_key=True, autoincrement=True)
    users_id = Column(Integer, ForeignKey('web_users.users_id'), nullable = True)
    symbol = Column(String(20), nullable = False)
    type = Column(String(255), nullable = False)
    percent = Column(Float, nullable = True)
    enabletype = Column(Boolean, nullable=True)
    create_date = Column(DateTime,  nullable = True)
    modified_date = Column(DateTime,  nullable = True)

    userst = relationship("User", foreign_keys=[users_id], backref=backref("stockwatchlist"))

    def __repr__(self):
        return self.symbol
