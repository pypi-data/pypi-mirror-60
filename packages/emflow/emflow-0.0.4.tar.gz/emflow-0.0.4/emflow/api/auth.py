import os,subprocess
from flask import Blueprint, current_app, g, redirect, request, session, url_for, jsonify
from flask_httpauth import HTTPBasicAuth
from ..db.models import User
from sqlalchemy.orm import joinedload

prefix = '/api/v1/auth'
bp = Blueprint('auth', __name__, url_prefix=prefix)
auth = HTTPBasicAuth()

# login
@auth.verify_password
def verify_password(username_or_token, password):
    if request.path == prefix+"/login":
        user = User.query.filter_by(name=username_or_token).first()
        if user:
            cmd = os.path.join(current_app.root_path, 'scripts/auth/run_su.sh')
            sub = subprocess.run('{} "" {} {}'.format(cmd,user.name,password),shell=True)
            if sub.returncode != 0:
                return False
        else:
            return False
    else:
        user = User.verify_auth_token(username_or_token)
        if not user:
            return False
    g.user = user
    return True

@bp.route('/login',methods=['POST'])
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return {"token":token,"user":g.user}

# users
@bp.route('/users',methods=['POST'])
@auth.login_required
def get_users():
    users = User.query.options(joinedload(User.projects)).all()
    #current_app.logger.info(users)
    return {user.id:user for user in users}


