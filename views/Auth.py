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


class AuthLoginHandler(BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.asynchronous
    def get(self):
        my_url = (self.request.protocol + "://" + self.request.host +
                  "/auth/login?next=" +
                  tornado.escape.url_escape(self.get_argument("next", "/")))
        if self.get_argument("code", False):
            self.get_authenticated_user(
                redirect_uri=my_url,
                client_id=self.settings["facebook_api_key"],
                client_secret=self.settings["facebook_secret"],
                code=self.get_argument("code"),
                callback=self._on_auth)
            return
        self.authorize_redirect(redirect_uri=my_url,
                                client_id=self.settings["facebook_api_key"])

    def _on_auth(self, user):
        if not user:
            raise tornado.web.HTTPError(500, "Facebook auth failed")

        # somewhere here i need to save 

        test_user = self.application.mongodb.users.find_one({'_id':user['id']})

        if test_user:
            self.set_secure_cookie("yahoohackday2013", tornado.escape.json_encode(user))
            self.redirect(self.get_argument("next", "/"))
        else:
            user_doc = user
            user_doc['_id'] = user['id']
            save_user = self.application.mongodb.user.save(user_doc)
            self.set_secure_cookie("yahoohackday2013", tornado.escape.json_encode(user))
            self.redirect(self.get_argument("next", "/"))


class AuthLogoutHandler(BaseHandler, tornado.auth.FacebookGraphMixin):
    def get(self):
        self.clear_cookie("yahoohackday2013")
        self.redirect(self.get_argument("next", "/"))