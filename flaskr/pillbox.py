from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.mongodb import get_db, get_users
from flaskr.schema import days_of_the_week
import json
from bson.objectid import ObjectId
import time

bp = Blueprint('pillbox', __name__)


@bp.route('/')
def index():
    user_id = session.get('user_id')
    if user_id:
        print(user_id)
        db = get_db()
        pills = db['pills']
        users =  db['users']
        user = users.find_one(ObjectId(str(user_id)))
        pillbox_list = user['pillbox']
        pillbox = join_pillbox(pillbox_list)

        pill_collection = db['pills'].find()

        return render_template('pillbox/index.html', pillbox=pillbox, pill_collection=pill_collection)
    else:
        return redirect(url_for('auth.login'))

@bp.route('/quiz')
def quiz():
    user_id = session.get('user_id')
    if user_id:
        return render_template('pillbox/quiz.html')
    else:
        return redirect(url_for('auth.login'))

@bp.route('/calendar')
def calendar():
    user_id = session.get('user_id')
    if user_id:
        return render_template('pillbox/calendar.html')
    else:
        return redirect(url_for('auth.login'))

@bp.route('/settings')
def settings():
    user_id = session.get('user_id')
    if user_id:
        return render_template('pillbox/settings.html')
    else:
        return redirect(url_for('auth.login'))

def join_pillbox(pillbox_list, days=days_of_the_week):
    db = get_db()
    pillbox = []

    for day, name in enumerate(days):
        day = pillbox_list[day]
        for index, pill in enumerate(day):
            pill_obj = db['pills'].find_one( pill['pill_id'] )
            pill_obj['time'] = pill['time']
            day[index] = pill_obj

        #sorted_day = sorted( (time.strptime(pill['time'], "%H:%M:%S") for pill in day), reverse=True)
        sorted_day = sorted(day, key = lambda pill: pill['time'], reverse=False) 

        data = { 'name': name, 'pills': sorted_day }
        pillbox.append(data)
    return pillbox
