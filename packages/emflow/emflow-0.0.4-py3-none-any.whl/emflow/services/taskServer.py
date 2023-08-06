import os,shutil,json
from functional import seq
from ..db import localModels
from sqlalchemy.exc import IntegrityError
from flask import current_app
from ..tasks import make_celery
from .extract import readStar,readAln,saveStar,extractPick
import numpy as np
from celery import signature


CONF_DIR = '.yx/conf'
CONF_CMDS_FILE = 'cmds.json'
MODULES = ['Movies','MotionCor','CTF','Pick','Extract']

######################
### conf functions ###
######################

def init_conf(projectDir):
    # copy conf files
    cdir = os.path.join(projectDir,CONF_DIR)
    if(not os.path.exists(cdir)): os.makedirs(cdir)
    cmdsFilePath = os.path.join(cdir,CONF_CMDS_FILE)
    if(not os.path.exists(cmdsFilePath)):
        shutil.copyfile(os.path.join(current_app.root_path,'scripts/conf',CONF_CMDS_FILE),cmdsFilePath)
    # create local db
    localModels.create_all(cdir)

def get_conf(projectDir):
    res = {}
    with open(os.path.join(projectDir,CONF_DIR,CONF_CMDS_FILE),'r') as f:
        res = json.load(f)
    return res

def set_conf(projectDir,conf):
    with open(os.path.join(projectDir,CONF_DIR,CONF_CMDS_FILE),'w') as f:
        json.dump(conf,f)

######################
### cmds functions ###
######################

def read_cmd_json_str(projectDir):
    rawCmdStr = ""
    with open(os.path.join(projectDir,CONF_DIR,CONF_CMDS_FILE),'r') as f:
        rawCmdStr=f.read()
    app_dir = current_app.config['APP_DIR']
    cmds = json.loads(rawCmdStr.replace('${app_dir}',app_dir))

    cmdDict={}
    for section,models in cmds.items():
        if section!='_current':
            model = models[cmds['_current'].get(section,'default')]
            if('cmd_before' in model):
                cmdBefore = model['cmd_before'].strip(';')+';'
            else:
                cmdBefore = ''

            cmdAfter = model.get('cmd_after','').strip(';')
            argStr = seq(model.get('args',[])).map(lambda a:f"{a['name']} {a['value']}")\
                .reduce(lambda x,y:f"{x} {y}",'')
            cmd = f"{model['cmd']} {argStr};"
            cmdDict[section] = f"cd {projectDir};{cmdBefore} {cmd} {cmdAfter}"

    return json.dumps(cmdDict)

# def read_cmd(projectDir,module,name):
#     cmdStr = read_cmd_json_str(projectDir)
#     cmds = json.load(cmdStr.format(name=name))
#     return cmds[module]

######################
### task functions ###
######################

def store_task(projectDir,node,modules,name,test):
    ids = []
    while node.parent:
      ids.append(node.id)
      node = node.parent
    ids.append(node.id)
    ids.reverse()
    module_ids = dict(zip(modules,ids))
    extract_id=module_ids['Pick'] if 'Pick' in module_ids else ''
    task=localModels.Tasks(name=name,id=ids[0],ids=ids,modules=modules,test=test,extract_id=extract_id)
    localDir = os.path.join(projectDir,CONF_DIR)
    for s in localModels.yield_local_session(localDir):
        try:
            s.add(task)
            s.commit()
        except IntegrityError:
            s.rollback()
            s.query(localModels.Tasks).filter_by(name=name).update({'id':task.id,'ids':task.ids,'modules':task.modules,'test':task.test,'extract_id':task.extract_id})
            s.commit()

def get_tasks_status(projectDir):
    localDir = os.path.join(projectDir,CONF_DIR)
    celery = make_celery(current_app)
    res = {}
    for s in localModels.yield_local_session(localDir):
        tasks = s.query(localModels.Tasks).all()
        for task in tasks:
            if task.modules and task.ids:
                mod_id_dict = dict(zip(task.modules,task.ids))
                ids_dict = {m:mod_id_dict.get(m,'0') for m in MODULES}
                ids_dict['Movies'] = task.movies_id if task.movies_id else ''
                ids_dict['Extract'] = task.extract_id if task.extract_id else ''
                task_res = {mod:celery.AsyncResult(id).state for mod,id in ids_dict.items()}
                res[task.name] = task_res
    return res

def build_chain_signature(projectDir,module,name,cmd):
    chain = signature('shell.cmd',args=(cmd,),immutable=True,queue='default')
    if(module=='CTF'):
        chain |= signature('shell.combine_ctf_star',args=(projectDir,name),immutable=True,queue='default')
    elif(module=='Pick'):
        chain |= signature('shell.trans_picks',args=(projectDir,name),immutable=True,queue='default')
        chain |= signature('shell.count_picks',args=(projectDir,name),immutable=True,queue='default')
        chain |= signature('shell.extract_pick',args=(projectDir,name),immutable=True,queue='default')
    return chain

def run_tasks(projectDir,modules,names):
    cmdStr = read_cmd_json_str(projectDir)
    celery = make_celery(current_app)
    for name in names:
        cmds = json.loads(cmdStr.replace('${name}',name))
        chain = seq(modules)\
            .map(lambda m:build_chain_signature(projectDir,m,name,cmds[m]))\
            .reduce(lambda x,y:x|y)
        res = chain.apply_async()
        store_task(projectDir,res,modules,name,True)

def run_mrc2png(projectDir):
    localDir = os.path.join(projectDir,CONF_DIR)
    celery = make_celery(current_app)
    names = seq(os.listdir(os.path.join(projectDir,'Movies')))\
        .map(lambda d:os.path.splitext(d))\
        .filter(lambda c:c[1] in ['.mrc','.mrcs'])\
        .map(lambda c:c[0])\
        .to_list()
    for s in localModels.yield_local_session(localDir):
        tasks = s.query(localModels.Tasks).all()
        for task in tasks:
            if not task.movies_id:
                res = signature('shell.mrc2png',args=(projectDir,task.name),immutable=True,queue='default').apply_async()
                task.movies_id = res.id
            names.remove(task.name)
        for name in names:
            res = signature('shell.mrc2png',args=(projectDir,name),immutable=True,queue='default').apply_async()
            task = localModels.Tasks(name=name,id=res.id)
            s.add(task)
        s.commit()

def run_count_extract(projectDir,name):
    localDir = os.path.join(projectDir,CONF_DIR)
    celery = make_celery(current_app)
    chain = signature('shell.count_picks',args=(projectDir,name),immutable=True,queue='default')
    chain |= signature('shell.extract_pick',args=(projectDir,name),immutable=True,queue='default')
    res = chain.apply_async()
    for s in localModels.yield_local_session(localDir):
        s.query(localModels.Tasks).filter_by(name=name).update({'extract_id':res.id})



######################
### star functions ###
######################

def get_motion_shift_from_aln(filePath):
    values = map(lambda x:(float(x[1]),float(x[2])),readAln(filePath)['globalShift'].values())
    x,y = zip(*values)
    return (np.var(x)+np.var(y))/2

def combine_ctf_star_result(projectDir,name):
    localDir = os.path.join(projectDir,CONF_DIR)
    # star data
    filePath = os.path.join(projectDir,'CTF',f"{name}_gctf.star")
    star = readStar(filePath)[0]
    u=float(star['DefocusU'])
    v=float(star['DefocusV'])
    # shift data
    alnFilePath = os.path.join(projectDir,'MotionCor',f"{name}.aln")
    shift = get_motion_shift_from_aln(alnFilePath)
    # insert to project local db
    for s in localModels.yield_local_session(localDir):
        statistic = localModels.Statistics(name=name,df=(u+v)/2,astig=abs(u-v),shift=shift,fit=star['FinalResolution'],mark='good',picks=0)
        try:
            s.add(statistic)
            s.commit()
        except IntegrityError:
            s.rollback()
            s.query(localModels.Statistics).filter_by(name=name).update({'df':statistic.df,'astig':statistic.astig,'shift':statistic.shift,'fit':statistic.fit})
            s.commit()

# def combine_ctf_star_results(projectDir):
#     localDir = os.path.join(projectDir,CONF_DIR)
#     ctfDir = os.path.join(projectDir,'CTF')
#     files = filter(lambda x:x.endswith('_gctf.star'),os.listdir(ctfDir))
#     for s in localModels.yield_local_session(localDir):
#         for file in files:
#             path = os.path.join(ctfDir,file)
#             star = readStar(path)[0]
#             u=float(star['DefocusU'])
#             v=float(star['DefocusV'])
#             alnFilePath = os.path.join(projectDir,'MotionCor',f"{file[:-10]}.aln")
#             shift = get_motion_shift_from_aln(alnFilePath)
#             statistic = Statistics(name,df=(u+v)/2,astig=abs(u-v),shift=shift,fit=star['FinalResolution'],mark='good',picks=0)
#             try:
#                 s.add(statistic)
#                 s.commit()
#             except IntegrityError:
#                 s.rollback()
#                 s.query(localModels.Statistics).filter_by(name=name).update({'df':statistic.df,'astig':statistic.astig,'shift':statistic.shift,'fit':statistic.fit})
#                 s.commit()
#             #os.remove(path)

def convert_pick_star(projectDir,name):
    readfilePath = os.path.join(projectDir,'Pick',name+"_automatch.star")
    stars = readStar(readfilePath)
    def auto(star):
        star['auto']=1
        return star
    savefilePath = os.path.join(projectDir,'Pick',name+".star")
    saveStar(savefilePath,list(map(auto,stars)))

def count_picks(projectDir,name):
    filePath = os.path.join(projectDir,'Pick',name+".star")
    picks = len(readStar(filePath))
    localDir = os.path.join(projectDir,CONF_DIR)
    for s in localModels.yield_local_session(localDir):
        s.query(localModels.Statistics).filter_by(name=name).update({'picks':picks})
        s.commit()


######################
### view functions ###
######################

def update_marks(projectDir,marks):
    localDir = os.path.join(projectDir,CONF_DIR)
    for s in localModels.yield_local_session(localDir):
        for mark in marks:
            s.query(localModels.Statistics).filter_by(name=mark['name']).update({'mark':mark['mark']})
        s.commit()


def clear(projectDir):
    cdir = os.path.join(projectDir,CONF_DIR)
    localModels.drop_all(cdir)

def get_statistics(projectDir):
    localDir = os.path.join(projectDir,CONF_DIR)
    stats = []
    for s in localModels.yield_local_session(localDir):
        stats = s.query(localModels.Statistics).all()
    return stats

