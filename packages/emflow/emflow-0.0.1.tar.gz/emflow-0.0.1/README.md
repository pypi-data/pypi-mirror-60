# BioFlow

BioFlow aim to making the data processing of electron microscope easier.
It includes process,2d,3d sections.

### Deployment

1. Virtual environment (Optional)

   ```shell script
   mkdir myproject
   cd myproject
   python3 -m venv venv
   #进入虚拟环境
   . venv/bin/activate
   #退出虚拟环境
   deactivate
   ```

2. Install

   ```shell script
   pip install -e . 
   ```

3. Config

   Your config.py looks like
   ```python
   import os
   
   SECRET_KEY='dev'
   SQLALCHEMY_DATABASE_URI='sqlite:////'+os.path.join(os.path.abspath(os.path.dirname(__file__)), 'bioflow.sqlite')
   SQLALCHEMY_TRACK_MODIFICATIONS = False
   CELERY_BROKER_URL='redis://localhost:6379'
   CELERY_RESULT_BACKEND='redis://localhost:6379'
   APP_DIR = '/app/app'
   ```

4. Run

   ```shell script
   export FLASK_APP=bioflow
   export FLASK_ENV=development
   export BIOFLOW_SETTINGS=/your/path/to/config.py
   flask init-db 
   flask run
   
   docker run -d --name bioflow_redis -p 6379:6379 redis
   
   celery -A bioflow.tasks.shell worker -Q default -c 1 -l info
   
   ```