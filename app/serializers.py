# -*- coding: utf-8 -*-

from flask import Flask, jsonify
from marshmallow import Schema, fields, ValidationError, pre_load
from marshmallow_sqlalchemy import ModelSchema
from collections import OrderedDict

from app.server import app,  api, ma, mail, flask_bcrypt
from app1 import models

class UserSerializerSQ(ModelSchema):
    class Meta:
        model = models.User
        sqla_session = models.db_session

class UserSerializer(Schema):
    users_id = fields.Int()
    serviceprovider = fields.Str()
    username = fields.Str()
    email = fields.Str()
    mobilenumber = fields.Str()
    descriptions = fields.Str()
    active = fields.Boolean()
    paidservice = fields.Boolean()
    amount = fields.Float()
    last_payment_date = fields.DateTime()
    create_date = fields.DateTime()
    modified_date = fields.DateTime()
    login_date = fields.DateTime()

class ServiceProviderSerializer(Schema):
    serviceprovider_id  = fields.Int()
    name = fields.Str()

class StockWatchlistSerializer(Schema):
    id = fields.Int()
    symbol = fields.Str()
    type =  fields.Str()
    percent = fields.Float()
    enabletype = fields.Int()
