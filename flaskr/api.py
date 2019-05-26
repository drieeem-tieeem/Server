from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.mongodb import get_db, get_users
from flaskr.schema import days_of_the_week
import json
from bson.objectid import ObjectId

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/test', methods=['POST'])
def test():
    user_id = session.get('user_id')
    #if user_id:
    data = request.form
    result = ""
    for key in data.keys():
        for value in data.getlist(key):
            result += (str(key)+" : "+str(value))

    
    return str(dict(data))
    #else:
    #    return redirect(url_for('auth.login'))