#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

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

# custom views
from views.Basehandler import BaseHandler
from views.Console import Console, ConsoleMultiple, ConsoleMultiple2
from views.Suggestions import Suggestions
from views.YQL import YQL
from views.StaticViews import LandingPageHandler
from views.Auth import AuthLoginHandler, AuthLogoutHandler
from views.Recipes import Recipes

define("port", default=8888, help="run on the given port", type=int)
define("facebook_api_key", help="your Facebook application API key",
       default="428024760630347")
define("facebook_secret", help="your Facebook application secret",
       default="645680350c08b3528f2cbce5cdd357a3")

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", LandingPageHandler),
            (r"/console", Console),
            (r"/console2", ConsoleMultiple),
            (r"/console3", ConsoleMultiple2),
            (r"/yql", YQL),
            (r"/auth/login", AuthLoginHandler),
            (r"/auth/logout", AuthLogoutHandler),
            (r"/suggestions", Suggestions),
            (r"/recipe", Recipes)
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            login_url="/auth/login",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            facebook_api_key=options.facebook_api_key,
            facebook_secret=options.facebook_secret,
            debug=True,
            autoescape=None,
            site_title="Open Data on YQL"
        )
        conn = pymongo.Connection("localhost", 27017)
        self.mongodb = conn["hackday_test"]
        tornado.web.Application.__init__(self, handlers, debug=True)
        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
