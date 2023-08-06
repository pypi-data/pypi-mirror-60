import os
from . import make_celery
from .. import create_app
from ..services.taskServer import combine_ctf_star_result,count_picks,convert_pick_star
from ..services.extract import extractPick,mrc2png

from subprocess import run,PIPE

celery = make_celery(create_app())

@celery.task(name='shell.mrc2png')
def mrc_to_png(pdir,name):
    filePath = os.path.join(pdir,'Movies',name+'.mrc')
    mrc2png(filePath)

@celery.task(name='shell.cmd')
def cmd(cmd):
    sub = run(cmd,shell=True,stdout=PIPE)
    returncode,out,err=sub.returncode,sub.stdout,sub.stderr
    print(returncode,out,err)

@celery.task(name='shell.combine_ctf_star')
def combine_ctf_star(pdir,name):
    combine_ctf_star_result(pdir,name)

@celery.task(name='shell.trans_picks')
def pick_trans_picks(pdir,name):
    convert_pick_star(pdir,name)

@celery.task(name='shell.count_picks')
def pick_count_picks(pdir,name):
    count_picks(pdir,name)

@celery.task(name='shell.extract_pick')
def extract_mrc_pick(pdir,name):
    mrcFilePath = os.path.join(pdir,'MotionCor',name+".mrc")
    starFilePath = os.path.join(pdir,'Pick',name+".star")
    extractPick(mrcFilePath,starFilePath)
