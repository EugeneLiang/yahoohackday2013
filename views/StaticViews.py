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

import requests

from views.Basehandler import BaseHandler

class LandingPageHandler(BaseHandler):
	def get(self):
		user = self.get_current_user()
		self.render("landing_marketing.html", user=user)


