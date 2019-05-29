from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.mongodb import get_db, get_users
from flaskr.schema import days_of_the_week
import json
from bson.objectid import ObjectId

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
        return render_template('pillbox/index.html', pillbox=pillbox)
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
        for collection in day:
            pills = collection['pills']
            for index, pill in enumerate(pills):
                pill_obj = db['pills'].find_one(pill)
                pills[index] = pill_obj
        data = { 'name': name, 'pills': day }
        pillbox.append(data)
    return pillbox
