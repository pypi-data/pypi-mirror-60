import os,subprocess,shutil,json,base64
from flask import Response, Blueprint, current_app, g, redirect, request, session, url_for, jsonify
from sqlalchemy.orm import joinedload
from functional import seq
from .auth import auth
from ..db import db
from ..db.models import User,Project
from ..tasks import make_celery
from ..services import taskServer
from ..services.extract import readStar,saveStar


prefix = '/api/v1/project'
bp = Blueprint('project', __name__, url_prefix=prefix)


@bp.route('/create',methods=['POST'])
@auth.login_required
def create_project():
    try:
        form=request.json['projectForm']
        project = Project(user_id=g.user.id,name=form['name'],directory=form['directory'],args=form['args'])
        db.session.add(project)
        db.session.commit()
        taskServer.init_conf(form['directory'])
        return 'done'
    except KeyError:
        return 'none'


@bp.route('/png')
@auth.login_required
def png():
    try:
        path=request.args['path']
    except KeyError:
        path="{}/{}/{}.{}.png".format(request.args['projectDir'],request.args['module'],request.args['name'],request.args['ext'])
    with open(path, 'rb') as f:
        image = f.read()
    return 'data:image/png;charset=utf-8;base64,'+base64.b64encode(image).decode('utf-8')


@bp.route('/clear',methods=['POST'])
@auth.login_required
def clear():
    pdir = request.json['projectDir']
    taskServer.clear(pdir)
    return 'done'


@bp.route('/test',methods=['POST'])
@auth.login_required
def run_test():
    pdir = request.json['projectDir']
    taskServer.init_conf(pdir) # mark sure exist conf files
    names = request.json['names'][:5]
    modules = request.json['modules']
    taskServer.run_tasks(pdir,modules,names)
    return "done"


@bp.route('/overview')
@auth.login_required
def page_overview():
    pdir = request.values['projectDir']
    taskServer.init_conf(pdir) # mark sure exist conf files
    status = taskServer.get_tasks_status(pdir)
    taskServer.run_mrc2png(pdir)
    stat_dict = {stat.name:stat for stat in taskServer.get_statistics(pdir)}
    files = seq(os.listdir(os.path.join(pdir,'Movies')))\
        .map(lambda d:os.path.splitext(d))\
        .filter(lambda c:c[1] in ['.mrc','.mrcs'])\
        .map(lambda c:{
            'name':c[0],
            'Movies':status[c[0]]['Movies'] if(c[0] in status) else 'PENDING',
            'MotionCor':status[c[0]]['MotionCor'] if(c[0] in status) else 'PENDING',
            'CTF':status[c[0]]['CTF'] if(c[0] in status) else 'PENDING',
            'Mark':stat_dict[c[0]].mark if c[0] in stat_dict else 'good',
            'Pick':stat_dict[c[0]].picks if c[0] in stat_dict else 0,
            'Extract':status[c[0]]['Extract'] if(c[0] in status) else 'PENDING'
        }).order_by(lambda x: x['name'])
    return jsonify(list(files))


@bp.route('/conf')
@auth.login_required
def get_conf():
    pdir = request.values['projectDir']
    taskServer.init_conf(pdir) # mark sure exist conf files
    return taskServer.get_conf(pdir)


@bp.route('/conf',methods=['POST'])
@auth.login_required
def set_conf():
    pdir = request.json['projectDir']
    conf = request.json['conf']
    taskServer.init_conf(pdir) # mark sure exist conf files
    taskServer.set_conf(pdir,conf)
    return 'done'


@bp.route('/preprocess')
@auth.login_required
def page_preprocess():
    stats = taskServer.get_statistics(request.values['projectDir'])
    return jsonify(stats)


@bp.route('/preprocess/mark',methods=['POST'])
@auth.login_required
def set_mark():
    pdir = request.json['projectDir']
    marks = request.json['marks']
    taskServer.update_marks(pdir,marks)
    return 'done'


@bp.route('/pick')
@auth.login_required
def page_pick():
    stats = taskServer.get_statistics(request.values['projectDir'])
    return jsonify(stats)


@bp.route('/pick/mark')
@auth.login_required
def get_pick():
    pdir = request.values['projectDir']
    name = request.values['name']
    filePath = os.path.join(pdir,'Pick',name+".star")
    if(not os.path.exists(filePath)):
        return []
    else:
        stars = readStar(filePath)
        return jsonify(stars)


@bp.route('/pick/mark',methods=['POST'])
@auth.login_required
def set_pick():
    pdir = request.json['projectDir']
    name = request.json['name']
    stars = request.json['arr']
    filePath = os.path.join(pdir,'Pick',name+".star")
    saveStar(filePath,stars)
    taskServer.run_count_extract(pdir,name)
    return 'done'

