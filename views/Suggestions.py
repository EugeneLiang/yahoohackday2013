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

import sys
#sys.path.append("/Users/mrjedi/Documents/projects/hack")
from fsm import *
yqltableaddr='http://192.241.238.206/'


class Suggestions2(BaseHandler):
    def get(self):
        print "Suggestions"
        data = {}
        data['resultset'] = {}
        data['resultset']['result'] = []
        query = self.get_argument("q", "", True).replace(",", "")

        # matched here is to give u additional hints, such as which table is selected and which fields are already selected.
        # those that are "matched" should be removed from the new iteration of suggested tables, fields
        matched = self.get_argument("q", "", True).replace(",", "")
        print "query ", query # check if it is reserved word. if reserverd word, i can show it's associated relations
        print "matched ", matched
        table_names = ['USE','DESC','FROM','SHOW','TABLE','TABLES','TENANT']  
        variables_or_filers = ['AND','IN','OR','WHERE']



        # here i need to check for "matched" queries. For example, the user already selected a table and or fields, and we need to 
        # modify the dataset accordingly
        if matched in table_names:
            # i need to return the result
            if matched == "USE":
                # technically i need to query mongodb or whatever that returns me the possible list of tables
                data['resultset']['result'].append({"title":"http://192.241.238.206/testiculture.xml", "description":"iCulture dataset regarding artists", "type":"datasource"})
                data['resultset']['result'].append({"title":"http://192.241.238.206/testiculture.xml", "description":"iCulture dataset regarding artist 2", "type":"datasource"})
                data['resultset']['result'].append({"title":"http://192.241.238.206/testiculture.xml", "description":"iCulture dataset regarding artist 3", "type":"datasource"})

            else:
                pass
        elif matched in variables_or_filers:
            pass
        else:

            # this case is when 
            # show possible list of keywords and reserved words
            data['resultset']['result'].append({"title":"USE", "description":"We usually start with the USE keyword to select data source", "type":"YQL Keyword"})
            data['resultset']['result'].append({"title":"DESC", "description":"Describes the source of the data", "type":"YQL Keyword"})
            data['resultset']['result'].append({"title":"FROM", "description":"Describing FROM", "type":"YQL Keyword"})
            data['resultset']['result'].append({"title":"IN", "description":"Describing IN", "type":"YQL Keyword"})
            data['resultset']['result'].append({"title":"OR", "description":"Describing OR", "type":"YQL Keyword"})
            data['resultset']['result'].append({"title":"TABLE", "description":"Describing TABLE", "type":"YQL Keyword"})
            data['resultset']['result'].append({"title":"TABLES", "description":"Describing TABLES", "type":"YQL Keyword"})
            data['resultset']['result'].append({"title":"TENANT", "description":"Describing TENANT", "type":"YQL Keyword"})

        self.write(data)

    def post(self):
        pass

class Suggestions_backup(BaseHandler):
    def get(self):
        print "Suggestions"
        data = {}
        data['resultset'] = {}
        data['resultset']['result'] = []
        query = self.get_argument("query", "", True).replace(",", "")

        # matched here is to give u additional hints, such as which table is selected and which fields are already selected.
        # those that are "matched" should be removed from the new iteration of suggested tables, fields
        matched = self.get_argument("matched", "", True).replace(",", "")
        print "query ", query # check if it is reserved word. if reserverd word, i can show it's associated relations
        print "matched ", matched
        table_names = ['USE','DESC','FROM','SHOW','TABLE','TABLES','TENANT']  
        variables_or_filers = ['AND','IN','OR','WHERE']



        # here i need to check for "matched" queries. For example, the user already selected a table and or fields, and we need to 
        # modify the dataset accordingly
        if matched in table_names:
            # i need to return the result
            if matched == "USE":
                # technically i need to query mongodb or whatever that returns me the possible list of tables
                data['resultset']['result'].append({"title":"http://192.241.238.206/testiculture.xml AS mytable", "description":"iCulture dataset", "previous":matched})
                data['resultset']['result'].append({"title":"http://192.241.238.206/testiculture.xml AS mytable2", "description":"iCulture dataset","previous":matched})
                data['resultset']['result'].append({"title":"http://192.241.238.206/testiculture.xml AS mytable3", "description":"iCulture dataset","previous":matched})

            else:
                pass
        elif matched in variables_or_filers:
            pass
        else:
            # this case is when 
            # show possible list of keywords and reserved words
            data['resultset']['result'].append({"title":"USE", "description":"We usually start with the USE keyword to select data source"})
            data['resultset']['result'].append({"title":"DESC"})
            data['resultset']['result'].append({"title":"FROM"})
            data['resultset']['result'].append({"title":"IN"})
            data['resultset']['result'].append({"title":"OR"})
            data['resultset']['result'].append({"title":"TABLE"})
            data['resultset']['result'].append({"title":"TABLES"})
            data['resultset']['result'].append({"title":"TENANT"})

        self.write(data)

    def post(self):
        pass


class Suggestions_backup2(BaseHandler):
    def get(self):
        print "Suggestions"
        data = {}
        data['resultset'] = {}
        data['resultset']['result'] = []
        query = self.get_argument("query", "", True).replace(",", "")
        # matched here is to give u additional hints, such as which table is selected and which fields are already selected.
        # those that are "matched" should be removed from the new iteration of suggested tables, fields
        matched = self.get_argument("term", "", True).replace(",", "")
        print "query ", query # check if it is reserved word. if reserverd word, i can show it's associated relations
        print "matched ", matched
        table_names = ['USE','DESC','FROM','SHOW','TABLE','TABLES','TENANT']  
        variables_or_filers = ['AND','IN','OR','WHERE']

        if matched == "USE":
            data['resultset']['result'].append({"title":"http://192.241.238.206/testiculture.xml AS mytable", "description":"iCulture dataset", "previous":matched})
            data['resultset']['result'].append({"title":"http://192.241.238.206/testiculture.xml AS mytable2", "description":"iCulture dataset","previous":matched})
            data['resultset']['result'].append({"title":"http://192.241.238.206/testiculture.xml AS mytable3", "description":"iCulture dataset","previous":matched})     

        else:
            data['resultset']['result'].append({"title":"USE", "description":"We usually start with the USE keyword to select data source", "previous":matched})
            data['resultset']['result'].append({"title":"DESC", "previous":matched})
            data['resultset']['result'].append({"title":"FROM", "previous":matched})
            data['resultset']['result'].append({"title":"IN", "previous":matched})
            data['resultset']['result'].append({"title":"OR", "previous":matched})
            data['resultset']['result'].append({"title":"TABLE", "previous":matched})
            data['resultset']['result'].append({"title":"TABLES", "previous":matched})
            data['resultset']['result'].append({"title":"TENANT", "previous":matched})   
        # here i need to check for "matched" queries. For example, the user already selected a table and or fields, and we need to 
        # modify the dataset accordingly


        self.write(data)

class Suggestions(BaseHandler):
    def get(self):
        print "Suggestions"
        data = []
        query = self.get_argument("term", "")
        query = query.strip()
        # matched here is to give u additional hints, such as which table is selected and which fields are already selected.
        # those that are "matched" should be removed from the new iteration of suggested tables, fields
        matched = self.get_argument("query", "")
        #matched = matched.strip()
        print "query ", query # check if it is reserved word. if reserverd word, i can show it's associated relations
        print "matched ", matched
        table_names = ['USE','DESC','FROM','SHOW','TABLE','TABLES','TENANT']  
        variables_or_filers = ['AND','IN','OR','WHERE']

        if matched == "USE":
            data.append({"id":"http://192.241.238.206/testiculture.xml AS mytable","value":"http://192.241.238.206/testiculture.xml AS mytable", "description":"iCulture dataset", "previous":matched, "type":"datasource"})
            data.append({"id":"http://192.241.238.206/testiculture.xml AS mytable2","value":"http://192.241.238.206/testiculture.xml AS mytable", "description":"iCulture dataset","previous":matched, "type":"datasource"})
            data.append({"id":"http://192.241.238.206/testiculture.xml AS mytable3","value":"http://192.241.238.206/testiculture.xml AS mytable", "description":"iCulture dataset","previous":matched, "type":"datasource"})     
        else:
            data.append({"id":"USE","value":"USE", "description":"We usually start with the USE keyword to select data source", "previous":matched, "type":"keyword"})
            data.append({"id":"SELECT","value":"SELECT", "description":"SELECT is used to choose certain fields from the table you have named", "previous":matched, "type":"keyword"})
            data.append({"id":"*","value":"*", "description":"* all fields", "previous":matched, "type":"keyword"})
            data.append({"id":"WHERE","value":"WHERE", "description":"for specifying a condition", "previous":matched, "type":"keyword"})
            data.append({"id":"FROM","value":"FROM", "description":"FROM {tablename}", "previous":matched, "type":"keyword"})
            data.append({"id":"IN","value":"IN", "description":"a filter or condition", "previous":matched, "type":"keyword"})
            data.append({"id":"OR","value":"OR", "description":"Logic operator", "previous":matched, "type":"logic"})
            data.append({"id":"AND","value":"AND", "description":"Logic operator", "previous":matched, "type":"logic"})
            data.append({"id":"=","value":"=", "description":" a condition operator", "previous":matched, "type":"condition"})
            data.append({"id":"LIKE","value":"LIKE", "description":" a condition operator", "previous":matched, "type":"condition"})
        # here i need to check for "matched" queries. For example, the user already selected a table and or fields, and we need to 
        # modify the dataset accordingly


        self.write(json.dumps(selectFSM(matched)))


    def post(self):
        pass