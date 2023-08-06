import click,subprocess
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 导入依赖db的模型模块
from . import models

def update_users():
    bashCommand="cat /etc/passwd|grep -v nologin|grep -v halt|grep -v shutdown|grep /home|awk -F':' '{print $1}'"
    sub = subprocess.run(bashCommand,shell=True,stdout=subprocess.PIPE)
    out = str(sub.stdout,encoding='utf-8')
    if(sub.returncode==0 and len(out)):
        new_users = set(out.split()).difference(set([u.name for u in models.User.query.all()]))
        if len(new_users):
            for name in new_users:
                user = models.User(name=name)
                db.session.add(user)
            db.session.commit()
            click.echo('Updated users.')
        else:
            click.echo('Users already updated.')
    else:
        click.echo('no users.')

def init_db():
    db.drop_all()
    db.create_all()
    click.echo('Initialized the database.')

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    update_users()

@click.command('update-users')
@with_appcontext
def update_users_command():
    update_users()

def init_app(app):
    db.init_app(app)
    app.cli.add_command(init_db_command)
    app.cli.add_command(update_users_command)
