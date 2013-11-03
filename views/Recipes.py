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

class Recipes(BaseHandler):
    def get(self):
        # single recipe page
        # show social sharing stuff.
        user = self.get_current_user()
        recipe_id = self.get_argument("id", None)
        if recipe_id:
            
            recipe = self.application.mongodb.recipe.find_one({"_id":ObjectId(recipe_id)})
            self.render("recipe.html", recipe=recipe, user=user)
            
            #self.render("recipe.html", user=user)
        else:
            # simply show a list of recipes
            # all recipes
            recipes = self.application.mongodb.recipe.find()
            self.render("all_recipes.html", recipes=recipes, user=user)

            

    def post(self):
        # here i will receieve a post containing title and description
        # need to parse the #tags to create #tags
        current_user = self.get_current_user()
        title = self.get_argument("title")
        description = self.get_argument("description")
        yql_statement = self.get_argument("yql_statement")
        tags = []
        check_tags = description.split(" ")
        for t in check_tags:
            if "#" in t:
                tags.append(t)

        doc = {
            "owner": current_user,
            "title":title,
            "description":description,
            "yql_statement":yql_statement,
            "vote_count":0,
            "tags":tags
        }
        save_recipe = self.application.mongodb.recipe.save(doc,safe=True)
        if save_recipe:
            # redirect to single recipe page
            #self.redirect("/recipe?id="+save_recipe)
            data = {
                "success":True,
                "id":str(save_recipe)
            }
            self.write(json.dumps(data))
        else:
            # something went wrong
            data = {
                "success":False
            }
            self.write(json.dumps(data))

    def put(self):
        pass

    def delete(self):
        pass