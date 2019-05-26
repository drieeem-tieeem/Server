from pymongo import MongoClient 
import json
from bson.objectid import ObjectId
from bson.json_util import loads
from bson.json_util import dumps
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import time

from flaskr.schema import *
from flaskr.pillbox  import *
from flaskr.mongodb import *

from flask import Flask, current_app
app = Flask(__name__)

client = MongoClient() 
client = MongoClient('localhost', 27017) 
db = client['drieeem_tieeem'] 

def update_users_schema():
  with app.app_context():
    users_db = get_users()
    users = users_db.find()
    for user in users:
        user['pillbox'] = pillbox_template
        users_db.replace_one( {'_id':user['_id']} , user)

def seed_random_pillbox(username):
  with app.app_context():
    users_db = get_users()
    user = users_db.find_one({'username':username})
    user['pillbox'][5].append(create_pill_collection(str(time(9, 30, 00)), [ (db.pills.find_one())['_id'], (db.pills.find_one())['_id'] ] ))
    user['pillbox'][0].append(create_pill_collection(str(time(18, 00, 00)), [ (db.pills.find_one())['_id'] ]))
    users_db.replace_one( {'_id':user['_id']} , user)