from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, Response
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.pillbox import join_pillbox
from flaskr.mongodb import get_db, get_users, get_pills
from flaskr.schema import days_of_the_week, pillbox_template
from test import update_users_schema, seed_random_pillbox
import json
from bson.objectid import ObjectId

from datetime import datetime, date, time, timedelta

user_id_str = '5cc956a49a161a065410a707'    # hardcoded for now
#user_id_str = str(get_users().find_one()['_id'])

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/')
def help():
    return redirect("https://docs.google.com/document/d/1dj5l9ECxeb6rGSHC3TrvGe1i6L9Aw0ETqebiPQ_HobY/edit?usp=sharing", code=302)

@bp.route('/test/seed', methods=['GET'])
def seed_user():
    username = 'curtis'
    user = get_users().find_one({'username': username})
    if not user:
        user = {}
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

@bp.route('/pills/add', methods=['POST'])
@bp.route('/pills/create', methods=['POST'])
def create_pill():
    #user_id = session.get('user_id')
    pill = {}
    data = request.form

    if 'name' in data and data['name']: pill['name'] = data.getlist('name')[0]
    else: pill['name'] = 'Unknown Pill'
    if 'description' in data and data['description']: pill['description'] = data.getlist('description')[0]
    else: pill['description'] = 'No Description'
    if 'icon' in data and data['icon']: pill['icon'] = data.getlist('icon')[0]
    else: pill['icon'] = 'icons/pill.png'

    duplicate = get_pills().find_one( {'name':pill['name']} )
    if duplicate:
        return str("ERROR: Pill already exists")
    else:
        get_pills().insert(pill)
        return str(pill)

@bp.route('/pills/<name>', methods=['GET'])
def get_pill(name):
    exists = get_pills().find_one( {'name':name} )
    if exists:
        return str(exists)
    else:
        return str("ERROR: Pill does not exists")

@bp.route('/pills', methods=['GET'])
def get_all_pills():
    pills = get_pills().find()
    result = ""
    for pill in pills:
        result += str(pill) + "\n"
    return result

@bp.route('/pills/delete/<name>', methods=['GET'])
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

@bp.route('/pillbox/<day_index>', methods=['GET'])
def get_pillbox_day(day_index):
    try:
        day_index = int(day_index)
        if day_index not in range(7):
            return "ERROR: invalid day."
    except:
        return "ERROR: invalid day."
        
    user_profile = get_users().find_one({ '_id': ObjectId(user_id_str) }) #hardcoded user
    pillbox_list = user_profile['pillbox']
    day = pillbox_list[day_index]

    day_collection = {}
    for index, pill in enumerate(day):
        pill_obj = get_pills().find_one( pill['pill_id'] )
        time = pill['time']
        name = pill_obj['name']
        if time in day_collection:
            day_collection[time].append(name)
        else:
            day_collection[time] = [name]

    return str(day_collection)

@bp.route('/pillbox/today', methods=['GET'])
def get_pillbox_today():
    current_datetime = datetime.now()
    day_index = (current_datetime.weekday() + 1) % 7
    return get_pillbox_day(day_index)

@bp.route('/pillbox/set', methods=['GET'])
def set_taken_auto():

    current_datetime = datetime.now()
    current_time = current_datetime.time()
    current_day = (current_datetime.weekday() + 1) % 7
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

@bp.route('/pilltimes/<day_index>', methods=['GET'])
def get_pilltimes(day_index, single=False):
    try:
        day_index = int(day_index)
        if day_index not in range(7):
            return "ERROR: invalid day."
    except:
        return "ERROR: invalid day."
        
    user_profile = get_users().find_one({ '_id': ObjectId(user_id_str) }) #hardcoded user
    pillbox_list = user_profile['pillbox']
    time_list = []
    for pill in pillbox_list[day_index]:
        time = pill['time']
        if time not in time_list:
            time_list.append(time)

    time_list = sorted(time_list, key = lambda time: time, reverse=False)
    
    if single:
        current_time = datetime.now().time()
        for index, pill_time in enumerate(time_list):
            if current_time <= datetime.strptime(pill_time, "%H:%M:%S").time():
                return str({'time':time_list[index]})
        return "{}"
    else:
        return str(time_list)

@bp.route('/pilltimes/today', methods=['GET'])
def get_pilltimes_today(single=False):
    current_datetime = datetime.now()
    day_index = (current_datetime.weekday() + 1) % 7
    return get_pilltimes(day_index, single)
    
@bp.route('/pilltimes/now', methods=['GET'])
@bp.route('/pilltimes/next', methods=['GET'])
def get_pilltimes_next():
    return Response(get_pilltimes_today(single=True), mimetype='text/json')

def schedule_error_check(data):
    pill = {}
    # do error checking
    if 'name' in data and data['name']: 
        pill_name = data.getlist('name')[0]
        pill_obj = get_pills().find_one({ 'name' : pill_name })
        if not pill_obj:
            return False, "ERROR: Pill not found.", pill
        pill['name'] = pill_obj['name']
        pill['pill_id'] = pill_obj['_id']
    else:
        return False, "ERROR: No pill specified.", pill
    if 'day' in data and data['day']: 
        pill['day'] = data.getlist('day')[0]
        try:
            pill['day'] = int(pill['day'])
        except:
            return False, "ERROR: Incorrect day specification.", pill
    else:
        return False, "ERROR: No day specified.", pill
    if 'time' in data and data['time']: 
        pill['time'] = data.getlist('time')[0]
        try:
            datetime.strptime(pill['time'], "%H:%M:%S").time()
        except:
            return False, "ERROR: Incorrect time specification.", pill
    else:
        return False, "ERROR: No time specified.", pill
        
    return True, str(pill['pill_id']), pill

@bp.route('/schedule/add', methods=['POST'])
def schedule_add():
    data = request.form
    success, result, pill = schedule_error_check(data)
    if not success:
        return result

    pill_day_index = pill['day']
    pill_name = pill['name']
    pill.pop('day', None)
    pill.pop('name', None)

    #add to pillbox
    user_profile = get_users().find_one({ '_id': ObjectId(user_id_str) }) #hardcoded user
    pillbox_list = user_profile['pillbox']
    day = pillbox_list[pill_day_index]
    day.append(pill)
    pillbox_list[pill_day_index] = day
    get_users().find_one_and_update( {'_id':user_profile['_id']}, {'$set': {'pillbox': pillbox_list}})

    return "Successfully added " + pill_name + " on day " + str(pill_day_index) + " at " + pill['time']


@bp.route('/schedule/remove', methods=['POST'])
def schedule_remove():
    data = request.form
    success, result, pill = schedule_error_check(data)
    if not success:
        return result

    pill_day_index = pill['day']
    pill_name = pill['name']
    pill.pop('day', None)
    pill.pop('name', None)

    #remove from pillbox
    user_profile = get_users().find_one({ '_id': ObjectId(user_id_str) }) #hardcoded user
    pillbox_list = user_profile['pillbox']
    day = pillbox_list[pill_day_index]
    
    found = False
    for index, possiblity in enumerate(day):
        if possiblity['pill_id'] == pill['pill_id'] and possiblity['time'] == pill['time']:
            day.pop(index)
            found = True
    
    pillbox_list[pill_day_index] = day
    get_users().find_one_and_update( {'_id':user_profile['_id']}, {'$set': {'pillbox': pillbox_list}})
    
    if found:
        return 'Success'
    else:
        return 'No pill with these parameters was found.'

@bp.route('/schedule/clear/<day_index>', methods=['GET'])
def schedule_clear_day(day_index):
    try:
        day_index = int(day_index)
        if day_index not in range(7):
            return "ERROR: invalid day."
    except:
        return "ERROR: invalid day."
        
    user_profile = get_users().find_one({ '_id': ObjectId(user_id_str) }) #hardcoded user
    pillbox_list = user_profile['pillbox']
    pillbox_list[day_index] = []
    get_users().find_one_and_update( {'_id':user_profile['_id']}, {'$set': {'pillbox': pillbox_list}})

    return "Successfully cleared day " + str(day_index) + "."

@bp.route('/schedule/clear', methods=['GET'])
def schedule_clear_all():
    user_profile = get_users().find_one({ '_id': ObjectId(user_id_str) }) #hardcoded user
    get_users().find_one_and_update( {'_id':user_profile['_id']}, {'$set': {'pillbox': pillbox_template}})

    return "Successfully cleared entire schedule"
