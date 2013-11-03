# -*- coding: utf-8 -*-
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
import sys
sys.path.append("/Users/mrjedi/Documents/projects/hack")

from fsm import *

from views.Basehandler import BaseHandler

class YQL(BaseHandler):
    def get(self):
        # simply returns the results of the YQL query
        query_string = self.get_argument("query_string", None)
        print query_string

        sqlQueryStr=query_string.split(";")
        sqlQueryStr=sqlQueryStr[len(sqlQueryStr)-1]
        sqlQueryStr=sqlQueryStr.replace('Info.','')
        print sqlQueryStr

        #data = [{"success":"True"}]
       # data = []
       # _data = requests.get("http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20geo.places.parent%20where%20child_woeid%20in%20(select%20woeid%20from%20geo.places%20where%20text%3D%22san%20francisco%2C%20ca%22)&format=json&diagnostics=true&callback=").json()
       # data.append(_data['query']['results']['place'])
        result=testMYSQL(sqlQueryStr);
        self.write(json.dumps(result['result']))


    def post(self):
        pass