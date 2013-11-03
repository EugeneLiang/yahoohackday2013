import os.path
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
import json 
from json import JSONEncoder

import pymongo
from bson.objectid import ObjectId
from bson.json_util import dumps



class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_json = self.get_secure_cookie("yahoohackday2013")
        if not user_json: return None
        return tornado.escape.json_decode(user_json)