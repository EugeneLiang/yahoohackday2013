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

from views.Basehandler import BaseHandler

class ConsoleMultiple2(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # here is the actual multiple console
        user = self.get_current_user()
        self.render("jquery_multiple.html", user=user)

    def post(self):
        pass



class Console(BaseHandler):

    def get(self):
        self.render("_console.html")

    def post(self):
        pass


class ConsoleMultiple(BaseHandler):
    def get(self):
        self.render("_multiple.html")

    def post(self):
        pass

