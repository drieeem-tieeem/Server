from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.pillbox import join_pillbox
from flaskr.mongodb import get_db, get_users, get_pills
from flaskr.schema import days_of_the_week
from test import update_users_schema, seed_random_pillbox
import json
from bson.objectid import ObjectId

from datetime import datetime, date, time, timedelta

user_id_str = '5cc956a49a161a065410a707'
bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/test/seed', methods=['GET'])
def seed_user():
    username = 'curtis'
    user = get_users().find_one({'username': username})
    if not user:
        user['_id'] = ObjectId(user_id_str)
        user['username'] = username
        user['password'] = 'pbkdf2:sha256:150000$jkwApNq5$6f2ee74568769791931a005c506afb2e585266373065a7f843977b9cdff38bad'
        get_users().insert(user)
    update_users_schema()
    seed_random_pillbox(username)
    return "User curtis data reset."

@bp.route('/test', methods=['POST'])
def test():
    #user_id = session.get('user_id')
    data = request.form
    result = ""
    for key in data.keys():
        for value in data.getlist(key):
            result += (str(key)+" : "+str(value)+"\n")
    #return str(dict(data))
    return result

@bp.route('/test/<name>', methods=['GET'])
def test_url(name):
    return name

@bp.route('/create-pill', methods=['POST'])
def create_pill():
    #user_id = session.get('user_id')
    pill = {}
    data = request.form

    if data['name']: pill['name'] = data.getlist('name')[0]
    else: pill['name'] = 'Unknown Pill'
    if data['description']: pill['description'] = data.getlist('description')[0]
    else: pill['description'] = 'No Description'
    if data['icon']: pill['icon'] = data.getlist('icon')[0]
    else: pill['icon'] = 'icons/pill.png'

    duplicate = get_pills().find_one( {'name':pill['name']} )
    if duplicate:
        return str("ERROR: Pill already exists")
    else:
        get_pills().insert(pill)
        return str(pill)

@bp.route('/get-pill/<name>', methods=['GET'])
def get_pill(name):
    exists = get_pills().find_one( {'name':name} )
    if exists:
        return str(exists)
    else:
        return str("ERROR: Pill does not exists")

@bp.route('/get-pills', methods=['GET'])
def get_all_pills():
    pills = get_pills().find()
    result = ""
    for pill in pills:
        result += str(pill) + "\n"
    return result

@bp.route('/delete-pill/<name>', methods=['GET'])
def delete_pill(name):
    exists = get_pills().find_one( {'name':name} )
    if exists:
        get_pills().remove( {'name':name} )
        return str(exists)
    else:
        return str("ERROR: Pill does not exists")

@bp.route('/pillbox', methods=['GET'])
def get_pillbox():
    user_profile = get_users().find_one({ '_id': ObjectId(user_id_str) }) #hardcoded user
    pillbox_list = user_profile['pillbox']
    
    pillbox = []
    for day in range(7):
        day = pillbox_list[day]
        for index, pill in enumerate(day):
            pill_obj = get_pills().find_one( pill['pill_id'] )
            pill_obj['time'] = pill['time']
            day[index] = pill_obj
        sorted_day = sorted(day, key = lambda pill: pill['time'], reverse=False)
        pillbox.append(sorted_day)

    return str(pillbox)

@bp.route('/pillbox/simple', methods=['GET'])
def get_pillbox_simple():
    user_profile = get_users().find_one({ '_id': ObjectId(user_id_str) }) #hardcoded user
    pillbox_list = user_profile['pillbox']
    
    pillbox = []
    for day in range(7):
        day = pillbox_list[day]
        for index, pill in enumerate(day):
            pill_obj = get_pills().find_one( pill['pill_id'] )
            stripped_pill = {
                'time': pill['time'],
                'name': pill_obj['name']
            }
            day[index] = stripped_pill
        sorted_day = sorted(day, key = lambda pill: pill['time'], reverse=False)
        pillbox.append(sorted_day)

    return str(pillbox)

@bp.route('/pillbox/timesheet', methods=['GET'])
def get_pillbox_timesheet():
    user_profile = get_users().find_one({ '_id': ObjectId(user_id_str) }) #hardcoded user
    pillbox_list = user_profile['pillbox']
    pillbox = []
    for day in range(7):
        day = pillbox_list[day]
        day_collections = {}
        for index, pill in enumerate(day):
            pill_obj = get_pills().find_one( pill['pill_id'] )
            time = pill['time']
            name = pill_obj['name']
            if time in day_collections:
                day_collections[time].append(name)
            else:
                day_collections[time] = [name]
        pillbox.append(day_collections)

    return str(pillbox)

@bp.route('/pillbox/set', methods=['GET'])
def set_taken_auto():

    current_datetime = datetime.now()
    current_time = current_datetime.time()
    current_day = current_datetime.weekday()
    current_week_start = current_datetime.date() - timedelta(current_day)

    current_hour_str = current_datetime.strftime("%H:%M:%S")

    user_profile = get_users().find_one({ '_id': ObjectId(user_id_str) }) #hardcoded user
    pillbox_list = user_profile['pillbox']
    for day_index in range(current_day):
        day = pillbox_list[day_index]
        for pill_index, pill in enumerate(day):

            pill_time = datetime.strptime(pill['time'], "%H:%M:%S").time()

            if pill_time < current_time:
                pill['taken'] = True
            day[pill_index] = pill
    
    get_users().find_one_and_update( {'_id':user_profile['_id']}, {'$set': {'pillbox': pillbox_list}})

    result = ""
    for item in pillbox_list:
        result += str(item) + "\n"
    return "CURRENT DAY: " + str(current_day) + " TIME: " + current_hour_str + "\n\n" + result


@bp.route('/pillbox/reset', methods=['GET'])
def reset_taken():
    user_profile = get_users().find_one({ '_id': ObjectId(user_id_str) }) #hardcoded user
    pillbox_list = user_profile['pillbox']
    for day in pillbox_list:
        for pill_index, pill in enumerate(day):
            if 'taken' in pill and pill['taken']:
                pill.pop('taken', None)
                day[pill_index] = pill

    get_users().find_one_and_update( {'_id':user_profile['_id']}, {'$set': {'pillbox': pillbox_list}})

    return "User " + user_profile['username'] + "'s pillbox has been reset."
