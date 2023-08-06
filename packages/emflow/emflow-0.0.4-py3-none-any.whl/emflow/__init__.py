import os,subprocess

from flask import Flask,request,g
from flask_cors import CORS
from . import db
from .db.models import User

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True,static_url_path='',static_folder='dist')
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:////'+os.path.join(app.instance_path, 'emflow.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS = False,
        CELERY_BROKER_URL='redis://localhost:6379',
        CELERY_RESULT_BACKEND='redis://localhost:6379',
        APP_DIR = '/app/app'
    )
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py',silent=True)
        app.config.from_envvar('EMFLOW_CONFIG',silent=True)
    else:
        app.config.from_mapping(test_config)
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    CORS(app)
    db.init_app(app)

    # main page
    @app.route('/')
    def hello():
        return app.send_static_file('index.html')

    # auth api
    from .api import auth
    app.register_blueprint(auth.bp)

    # project api
    from .api import project
    app.register_blueprint(project.bp)

    return app
