from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.mongodb import get_db, get_users, get_pills
from flaskr.schema import days_of_the_week
import json
from bson.objectid import ObjectId


#user_id_str = '5cc956a49a161a065410a707'
bp = Blueprint('api', __name__, url_prefix='/api')

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

@bp.route('/delete-pill/<name>', methods=['GET'])
def delete_pill(name):
    exists = get_pills().find_one( {'name':name} )
    if exists:
        get_pills().remove( {'name':name} )
        return str(exists)
    else:
        return str("ERROR: Pill does not exists")