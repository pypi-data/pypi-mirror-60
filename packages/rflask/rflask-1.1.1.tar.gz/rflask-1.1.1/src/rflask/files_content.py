# -*- coding: utf-8 -*-
"""
 __author__:  @haopeng_dong
 __datetime__:  2020/1/23
"""


def root_env_s():
    return """SECRET_KEY=not-so-secret
SEND_FILE_MAX_AGE_DEFAULT=0
"""


def root_env_example_s():
    return """# Environment variable overrides for local development
FLASK_APP=autoapp.py
FLASK_DEBUG=1
FLASK_ENV=development
DATABASE_URL=sqlite:////tmp/dev.db
GUNICORN_WORKERS=1
LOG_LEVEL=debug
SECRET_KEY=not-so-secret
# In production, set to a higher number, like 31556926
SEND_FILE_MAX_AGE_DEFAULT=0

"""


def root_gitignore_s():
    return """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# PEP 582; used by e.g. github.com/David-OConnor/pyflow
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# Pycharm
.idea

"""


def root_init_s():
    return """import sys
import pymysql

sys.path.append('.')
pymysql.install_as_MySQLdb()

"""


def root_app_s():
    return """# -*- coding: utf-8 -*-
\"\"\"Create an application instance.\"\"\"
from autoapp import create_app
from settings import Dev, Test, Pro

# app = create_app(Pro)
app = create_app(Dev)
# app = create_app(Test)

if __name__ == '__main__':
    app.run()

"""


def root_autoapp_s():
    return """# -*- coding: utf-8 -*-
\"\"\"The app module, containing the app factory function.\"\"\"
import logging
import sys

from flask import Flask

from applications import user
from applications.user.models import *
from extensions import (
    bcrypt,
    debug_toolbar,
    migrate,
    flask_redis,
    mail,
    logger,
    db
)
from scripts import commands
from applications.test.views import register_api_test


def create_app(config_object):
    \"\"\"Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    \"\"\"
    app = Flask(__name__)
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_api(app)
    register_shellcontext(app)
    register_commands(app)
    configure_logger(app)
    return app


def register_extensions(app):
    \"\"\"Register Flask extensions.\"\"\"
    bcrypt.init_app(app)
    db.init_app(app)
    debug_toolbar.init_app(app)
    migrate.init_app(app, db)
    flask_redis.init_app(app)
    mail.init_app(app)
    return None


def register_blueprints(app):
    \"\"\"Register Flask blueprints.\"\"\"
    app.register_blueprint(user.views.blueprint)
    return None


def register_api(app):
    \"\"\"Register Flask Api.\"\"\"
    register_api_test(app)
    return None


def register_shellcontext(app):
    \"\"\"Register shell context objects.\"\"\"

    def shell_context():
        \"\"\"Shell context objects.\"\"\"
        return {"db": db, "User": user.models.User}

    app.shell_context_processor(shell_context)


def register_commands(app):
    \"\"\"Register Click commands.\"\"\"
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)


def configure_logger(app):
    \"\"\"Configure loggers.\"\"\"
    handler = logging.StreamHandler(sys.stdout)
    if not app.logger.handlers:
        app.logger.addHandler(handler)
    logger.init_app(app)

"""


def root_compat_s():
    return """# -*- coding: utf-8 -*-
\"\"\"Python 2/3 compatibility module.\"\"\"
import sys

PY2 = int(sys.version[0]) == 2

if PY2:
    text_type = unicode  # noqa
    binary_type = str
    string_types = (str, unicode)  # noqa
    unicode = unicode  # noqa
    basestring = basestring  # noqa
else:
    text_type = str
    binary_type = bytes
    string_types = (str,)
    unicode = str
    basestring = (str, bytes)

"""


def root_database_s():
    return """# -*- coding: utf-8 -*-
\"\"\"Database module, including the SQLAlchemy database object and DB-related utilities.\"\"\"
from datetime import datetime

from compat import basestring
from extensions import db

# Alias common SQLAlchemy names
Column = db.Column
relationship = db.relationship


class CRUDMixin(object):
    \"\"\"Mixin that adds convenience methods for CRUD (create, read, update, delete) operations.\"\"\"

    @classmethod
    def create(cls, **kwargs):
        \"\"\"Create a new record and save it the database.\"\"\"
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        \"\"\"Update specific fields of a record.\"\"\"
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        \"\"\"Save the record.\"\"\"
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        \"\"\"Remove the record from the database.\"\"\"
        db.session.delete(self)
        return commit and db.session.commit()


class Model(CRUDMixin, db.Model):
    \"\"\"Base model class that includes CRUD convenience methods.\"\"\"

    __abstract__ = True


# From Mike Bayer's "Building the app" talk
# https://speakerdeck.com/zzzeek/building-the-app
class SurrogatePK(object):
    \"\"\"A mixin that adds a surrogate integer 'primary key' column named ``id`` to any declarative-mapped class.\"\"\"

    __table_args__ = {"extend_existing": True}

    id = Column(db.Integer, primary_key=True)
    create_time = Column(db.DateTime, default=datetime.now)
    update_time = Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    @classmethod
    def get_by_id(cls, record_id):
        \"\"\"Get record by ID.\"\"\"
        if any(
            (
                isinstance(record_id, basestring) and record_id.isdigit(),
                isinstance(record_id, (int, float)),
            )
        ):
            return cls.query.get(int(record_id))
        return None


def reference_col(
    tablename, nullable=False, pk_name="id", foreign_key_kwargs=None, column_kwargs=None
):
    \"\"\"Column that adds primary key foreign key reference.

    Usage: ::

        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
    \"\"\"
    foreign_key_kwargs = foreign_key_kwargs or {}
    column_kwargs = column_kwargs or {}

    return Column(
        db.ForeignKey(f"{tablename}.{pk_name}", **foreign_key_kwargs),
        nullable=nullable,
        **column_kwargs,
    )

"""


def root_docker_compose_s(project_name):
    return """version: "3"

services:

  %s:
    image: %s:v1.0.0
    ports:
      - "8000:8000"
    stdin_open: true
    tty: true
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - .:/deploy/%s
      - ./gunicorn.conf.py:/etc/gunicorn/conf.d/gunicorn.conf.py
      - ./supervisord.conf:/etc/supervisor/conf.d/supervisord.conf
    container_name: %s
    command: 'supervisord -c /etc/supervisor/conf.d/supervisord.conf'

""" % (project_name, project_name, project_name, project_name)


def root_docker_file_s(project_name):
    return """FROM python:3

RUN apt-get update && apt-get install -y supervisor
RUN pip3 install gunicorn -i https://mirrors.aliyun.com/pypi/simple/
RUN pip3 install setuptools -i https://mirrors.aliyun.com/pypi/simple/

ENV PYTHONIOENCODING=utf-8

# Build folder
RUN mkdir -p /deploy/%s
WORKDIR /deploy/%s
COPY requirements/prod.txt /deploy/%s/prod.txt
RUN pip3 install -r /deploy/%s/prod.txt -i https://mirrors.aliyun.com/pypi/simple/

# Setup supervisord
RUN mkdir -p /var/log/supervisor

""" % (project_name, project_name, project_name, project_name)


def root_extensions_s():
    return """# -*- coding: utf-8 -*-
\"\"\"Extensions module. Each extension is initialized in the app factory located in app.py.\"\"\"
from flask_bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail
from flask_migrate import Migrate
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy

from flask_ext.logger import Logger

bcrypt = Bcrypt()
db = SQLAlchemy()
migrate = Migrate()
debug_toolbar = DebugToolbarExtension()
flask_redis = FlaskRedis()
mail = Mail()
logger = Logger()

"""


def root_gunicorn_s():
    return """import multiprocessing

bind = '0.0.0.0:8000'
# bind = 'unix:/run/gunicorn.sock'
# workers = multiprocessing.cpu_count() * 2 + 1
workers = 2
# daemon = True
pidfile = '/run/gunicorn.pid'
loglevel = 'info'
errorlog = '/var/log/gunicorn_error.log'
accesslog = '/var/log/gunicorn_access.log'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

"""


def root_LICENSE_s():
    return """MIT License

Copyright (c) 2020 Deacone

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""


def root_Pipfile_s():
    return """[[source]]
name = "pypi"
#url = "https://pypi.org/simple"
url = "https://mirrors.aliyun.com/pypi/simple/"
verify_ssl = true

[dev-packages]
# Testing
pytest = "==5.3.4"
WebTest = '==2.0.33'
factory-boy = '==2.12.0'
pdbpp = '==0.10.2'
# Lint and code style
black = '==19.10b0'
flake8 = '==3.7.9'
flake8-blind-except = '==0.1.1'
flake8-debugger = '==3.2.1'
flake8-docstrings = '==1.5.0'
flake8-isort = '==2.8.0'
isort = '==4.3.21'
pep8-naming = '==0.9.1'

[packages]
flask = "==1.1.1"
flask-restful = "==0.3.7"
# Database
flask-sqlalchemy = "==2.4.1"
psycopg2-binary = "==2.8.4"
# Migrations
flask-migrate = "==2.5.2"
# Deployment
gevent = "==1.4.0"
gunicorn = ">=19.9.0"
supervisor = "==4.1.0"
# Auth
Flask-Login = "==0.4.1"
Flask-Bcrypt = "==0.7.1"
# Caching
Flask-Caching = ">=1.7.2"
# Debug toolbar
Flask-DebugToolbar = "==0.10.1"
# Environment variable parsing
environs = "==7.1.0"
flask-mail = ">=0.9.1"
flask-redis = ">=0.4.0"
werkzeug = "==0.16.0"
click = ">=7.0"
sqlalchemy = "==1.3.12"
pytest = "==5.3.3"
webtest = "==2.0.33"
factory-boy = "==2.12.0"
pdbpp = "==0.10.2"
black = "==19.10b0"
flake8 = "==3.7.9"
flake8-blind-except = "==0.1.1"
flake8-debugger = "==3.2.1"
flake8-docstrings = "==1.5.0"
flake8-isort = "==2.8.0"
isort = "==4.3.21"
pep8-naming = "==0.9.1"
pymysql = "*"

[requires]
python_version = "3.7"

"""


def root_readme_s():
    return """========================
Init flask restful api
========================

Init flask restful project with sqlalchemy, flask_restful, redis, mail, logger, bcrypt.
It will save your time from building base.

--------------------
How it works?
--------------------

Not Pipenv:

In your project root dir, open the terminal:

.. code-block:: text

    $ pip install -r requirements/dev.txt -i https://mirrors.aliyun.com/pypi/simple/
    $ python app.py

     * Serving Flask app "autoapp" (lazy loading)
     * Environment: dev
     * Debug mode: on
    2020-01-23 13:03:24,151 [4554636736:MainThread] [_internal.py:_internal:_log] [INFO]:  * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    2020-01-23 13:03:24,152 [4554636736:MainThread] [_internal.py:_internal:_log] [INFO]:  * Restarting with stat
    2020-01-23 13:03:24,600 [4616764864:MainThread] [_internal.py:_internal:_log] [WARNING]:  * Debugger is active!
    2020-01-23 13:03:24,604 [4616764864:MainThread] [_internal.py:_internal:_log] [INFO]:  * Debugger PIN: 186-303-110

Use Pipenv:

In your project root dir, open the terminal:

.. code-block:: text

    $ pip install pipenv -i https://mirrors.aliyun.com/pypi/simple/
    $ pipenv install --dev
    $ pipenv run python app.py

     * Serving Flask app "autoapp" (lazy loading)
     * Environment: dev
     * Debug mode: on
    2020-01-23 13:03:24,151 [4554636736:MainThread] [_internal.py:_internal:_log] [INFO]:  * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    2020-01-23 13:03:24,152 [4554636736:MainThread] [_internal.py:_internal:_log] [INFO]:  * Restarting with stat
    2020-01-23 13:03:24,600 [4616764864:MainThread] [_internal.py:_internal:_log] [WARNING]:  * Debugger is active!
    2020-01-23 13:03:24,604 [4616764864:MainThread] [_internal.py:_internal:_log] [INFO]:  * Debugger PIN: 186-303-110

--------
Init db
--------

.. code-block:: text

    $ flask db init
    $ flask db migrate
    $ flask db upgrade


-------------------
Deploy to docker
-------------------

In your project root dir, open the terminal:

.. code-block:: text

    $ git clone ***.git
    $ cd <your_project>
    $ docker-compose up

"""


def root_settings_s():
    return """# -*- coding: utf-8 -*-
\"\"\"Application configuration.
\"\"\"
import os

BASE_DIR = os.path.dirname(__file__)


class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'it-is-secret'

    # 数据库配置
    DB_HOST = ""
    DB_PORT = ""
    DB_DATABASE = ""
    DB_USER = ""
    DB_PASSWORD = ""
    SQLALCHEMY_DATABASE_URI = "mysql://{}:{}@{}:{}/{}".format(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_timeout': 10,    # 默认链接超时时长
        'pool_size': 10        # 数据库链接池大小
    }
    # 提供多库链接 使用其他库进行链接的时候需要使用bind指定那个库使用
    SQLALCHEMY_BINDS = {}
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # REDIS配置
    REDIS_CONFIGS = {
        "default": {
            "host": "",
            "port": "",
            "password": "",
        },
    }


class Pro(Config):
    ENV = 'product'


class Dev(Config):
    DEBUG = True
    ENV = 'dev'


class Test(Config):
    TESTING = True
    DEBUG = True
    ENV = 'test'

"""


def root_supervisord_s(project_name):
    return """[program:%s]
# pro
directory=/deploy/%s
command=gunicorn app:app -c /deploy/%s/gunicorn.conf.py

user=root
; autorestart=true
; redirect_stderr=true

[supervisord]
logfile=/var/log/supervisord.log
logfile_maxbytes=50MB
logfile_backups=5
loglevel=info
pidfile=/tmp/supervisord.pid                    ; pidfile location
nodaemon=true                                   ; run supervisord as a daemon
minfds=1024                                     ; number of startup file descriptors
minprocs=200                                    ; number of process descriptors

[supervisorctl]
serverurl=unix:///tmp/supervisor.sock

; [include]
; files = /etc/supervisor/conf.d/*.conf

""" % (project_name, project_name, project_name)


def root_setup_s(project_name, author, author_email, description):
    return """# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="%s",
    version="1.0.0",
    packages=find_packages(),
    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=[
        "click>=5.1",
        "flask==1.1.1"
    ],
    entry_points='''
        [console_scripts]
        rflask=src.commands:rflask
    ''',

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        "": ["*.md", "*.py"],
        # And include any *.msg files found in the "hello" package, too:
        "src": ["*.py"],
    },
    # metadata to display on PyPI
    author="%s",
    author_email="%s",
    description="%s",
    keywords="flask restful api init",
    url="https://github.com/Deacone/init-flask-restful-api",  # project home page, if any
    project_urls={
        # "Bug Tracker": "https://bugs.example.com/HelloWorld/",
        "Documentation": "https://github.com/Deacone/init-flask-restful-api",
        "Source Code": "https://github.com/Deacone/init-flask-restful-api",
    },
    classifiers=[
        "License :: mit :: MIT License",
        "Programming Language :: Python :: 3.6"

    ]

    # could also include long_description, download_url, etc.
)

""" % (project_name, author, author_email, description)


def applications_test_init_s():
    return """# -*- coding: utf-8 -*-
\"\"\"The test module.\"\"\"
from . import views
"""


def applications_test_models_s():
    return """# -*- coding: utf-8 -*-
\"\"\"Test models.\"\"\"
from database import (
    Column,
    Model,
    SurrogatePK,
    db,
    reference_col,
    relationship,
)


class Test(SurrogatePK, Model):
    \"\"\"A test model, more about models, please see the user model.\"\"\"

    __tablename__ = "test_model"
    name = Column(db.String(80), unique=True, nullable=False)

    def __init__(self, name, **kwargs):
        \"\"\"Create instance.\"\"\"
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        \"\"\"Represent instance as a unique string.\"\"\"
        return f"<Role({self.name})>"

"""


def applications_test_readme_s():
    return """============================
An example of register api.
============================
"""


def applications_test_views_s():
    return """# -*- coding: utf-8 -*-
\"\"\"Test views.\"\"\"

from flask_restful import Resource, Api

from utils import restful_util


def register_api_test(app):
    api = Api(app, prefix='/api/test')
    api.add_resource(Test, '/', endpoint='test')


class Test(Resource):
    def get(self):
        return restful_util.success()

"""


def applications_user_init_s():
    return """# -*- coding: utf-8 -*-
\"\"\"The user module.\"\"\"
from . import views
"""


def applications_user_models_s():
    return """# -*- coding: utf-8 -*-
\"\"\"User models.\"\"\"
import datetime as dt

from flask_login import UserMixin

from database import (
    Column,
    Model,
    SurrogatePK,
    db,
    reference_col,
    relationship,
)
from extensions import bcrypt


class Role(SurrogatePK, Model):
    \"\"\"A role for a user.\"\"\"

    __tablename__ = "roles"
    name = Column(db.String(80), unique=True, nullable=False)
    user_id = reference_col("users", nullable=True)
    user = relationship("User", backref="roles")

    def __init__(self, name, **kwargs):
        \"\"\"Create instance.\"\"\"
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        \"\"\"Represent instance as a unique string.\"\"\"
        return f"<Role({self.name})>"


class User(UserMixin, SurrogatePK, Model):
    \"\"\"A user of the app.\"\"\"

    __tablename__ = "users"
    username = Column(db.String(80), unique=True, nullable=False)
    email = Column(db.String(80), unique=True, nullable=False)
    #: The hashed password
    password = Column(db.LargeBinary(128), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    first_name = Column(db.String(30), nullable=True)
    last_name = Column(db.String(30), nullable=True)
    active = Column(db.Boolean(), default=False)
    is_admin = Column(db.Boolean(), default=False)

    def __init__(self, username, email, password=None, **kwargs):
        \"\"\"Create instance.\"\"\"
        db.Model.__init__(self, username=username, email=email, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        \"\"\"Set password.\"\"\"
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        \"\"\"Check password.\"\"\"
        return bcrypt.check_password_hash(self.password, value)

    @property
    def full_name(self):
        \"\"\"Full user name.\"\"\"
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        \"\"\"Represent instance as a unique string.\"\"\"
        return f"<User({self.username!r})>"

"""


def applications_user_readme_s():
    return """===================================
An example of register blueprint.
===================================
"""


def applications_user_views_s():
    return """# -*- coding: utf-8 -*-
\"\"\"User views.\"\"\"
from flask import Blueprint, jsonify
from flask_login import login_required
from flask import current_app

blueprint = Blueprint("user", __name__, url_prefix="/users", static_folder="../../static")


@blueprint.route("/")
# @login_required
def members():
    \"\"\"List members.\"\"\"
    return jsonify({
        'config': current_app.config.get('DATABASE_URI')
    })

"""


def exceptions_project_excepions_s():
    return """# -*- coding: utf-8 -*-
\"\"\"Project exceptions\"\"\"


class IllegalConfigEnvException(Exception):
    pass


class IllegalConditionException(Exception):
    pass


class IllegalConfigException(Exception):
    pass

"""


def flask_ext_logger_s():
    return """# -*- coding: utf-8 -*-
\"\"\"
 __author__:  @haopeng_dong
 __datetime__:  2020/1/19

 Flask logger module. as explained here: https://www.cnblogs.com/DeaconOne/p/11153810.html
\"\"\"

import logging
import os
from logging import StreamHandler
from logging.handlers import RotatingFileHandler

from flask.logging import default_handler

from settings import BASE_DIR

LOG_PATH = os.path.join(BASE_DIR, 'logs', 'all.log')

# 日志文件最大 100MB
LOG_FILE_MAX_BYTES = 100 * 1024 * 1024
# 轮转数量是 10 个
LOG_FILE_BACKUP_COUNT = 10


class Logger(object):

    def init_app(self, app):
        # 移除默认的handler
        app.logger.removeHandler(default_handler)

        formatter = logging.Formatter(
            '%(asctime)s [%(thread)d:%(threadName)s] [%(filename)s:%(module)s:%(funcName)s] '
            '[%(levelname)s]: %(message)s'
        )

        # 将日志输出到文件
        # 1 MB = 1024 * 1024 bytes
        # 此处设置日志文件大小为500MB，超过500MB自动开始写入新的日志文件，历史文件归档
        file_handler = RotatingFileHandler(
            filename=LOG_PATH,
            mode='a',
            maxBytes=LOG_FILE_MAX_BYTES,
            backupCount=LOG_FILE_BACKUP_COUNT,
            encoding='utf-8'
        )

        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)

        stream_handler = StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.INFO)

        for logger in (
                # 这里自己还可以添加更多的日志模块，具体请参阅Flask官方文档
                app.logger,
                logging.getLogger('sqlalchemy'),
                logging.getLogger('werkzeug')

        ):
            logger.addHandler(file_handler)
            logger.addHandler(stream_handler)

"""


def requirements_dev_s():
    return """# Everything the developer needs in addition to the production requirements
-r prod.txt

# Testing
pytest==5.3.3
WebTest==2.0.33
factory-boy==2.12.0
pdbpp==0.10.2

# Lint and code style
black==19.10b0
flake8==3.7.9
flake8-blind-except==0.1.1
flake8-debugger==3.2.1
flake8-docstrings==1.5.0
flake8-isort==2.8.0
isort==4.3.21
pep8-naming==0.9.1

"""


def requirements_prod_s():
    return """# Everything needed in production

# Flask
Flask==1.1.1
Werkzeug==0.16.0
click>=7.0

# Database
Flask-SQLAlchemy==2.4.1
SQLAlchemy==1.3.12
psycopg2-binary==2.8.4

# Migrations
Flask-Migrate==2.5.2

# Deployment
gevent==1.4.0
gunicorn>=19.9.0
supervisor==4.1.0

# Auth
Flask-Login==0.4.1
Flask-Bcrypt==0.7.1

# Caching
Flask-Caching>=1.7.2

# Debug toolbar
Flask-DebugToolbar==0.10.1

# Environment variable parsing
environs==7.1.0

# mail
flask_mail>=0.9.1

# redis
flask_redis>=0.4.0

# restful
flask-restful

"""


def scripts_commands_s():
    return """# -*- coding: utf-8 -*-
\"\"\"Click commands.\"\"\"
import os
from glob import glob
from subprocess import call

import click
import pytest

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, "tests")


@click.command()
def test():
    \"\"\"Run the tests.\"\"\"
    rv = pytest.main([TEST_PATH, "--verbose"])
    exit(rv)


@click.command()
@click.option(
    "-f",
    "--fix-imports",
    default=True,
    is_flag=True,
    help="Fix imports using isort, before linting",
)
@click.option(
    "-c",
    "--check",
    default=False,
    is_flag=True,
    help="Don't make any changes to files, just confirm they are formatted correctly",
)
def lint(fix_imports, check):
    \"\"\"Lint and check code style with black, flake8 and isort.\"\"\"
    skip = ["node_modules", "requirements", "migrations"]
    root_files = glob("*.py")
    root_directories = [
        name for name in next(os.walk(".."))[1] if not name.startswith(".")
    ]
    files_and_directories = [
        arg for arg in root_files + root_directories if arg not in skip
    ]

    def execute_tool(description, *args):
        \"\"\"Execute a checking tool with its arguments.\"\"\"
        command_line = list(args) + files_and_directories
        click.echo(f"{description}: {' '.join(command_line)}")
        # click.echo("%s: %s" % (description, ''.join(command_line)))
        rv = call(command_line)
        if rv != 0:
            exit(rv)

    isort_args = ["-rc"]
    black_args = []
    if check:
        isort_args.append("-c")
        black_args.append("--check")
    if fix_imports:
        execute_tool("Fixing import order", "isort", *isort_args)
    execute_tool("Formatting style", "black", *black_args)
    execute_tool("Checking code style", "flake8")

"""


def tests_test_applications_test_s():
    return """# -*- coding: utf-8 -*-
\"\"\"
 __author__:  @haopeng_dong
 __datetime__:  2020/1/28
\"\"\"
import flask
from app import app


def test_get():
    with app.test_client() as c:
        rv = c.get('/api/test/')
        json_data = rv.get_json()
        print('json_data:', json_data)
        assert json_data['code'] == 200000

"""


def utils_restful_util_s():
    return """# -*- coding: utf-8 -*-
\"\"\"
 __author__:  @haopeng_dong
 __datetime__:  2020/1/28

 Restful util.
\"\"\"
from flask import jsonify


class HttpCode(object):
    OK = 200000
    PARAMS_ERROR = 400000
    UNAUTH_ERROR = 400001
    FORBIDDEN_ERROR = 400003
    NOT_FOUND = 400004
    INTERNAL_SERVER_ERROR = 500000


def restful_result(code, message, data):
    return jsonify({
        "code": code,
        "message": message,
        "data": data or {}
    })


def success(message='操作成功', data=None):
    return restful_result(code=HttpCode.OK, message=message, data=data)


def params_error(message=""):
    return restful_result(code=HttpCode.PARAMS_ERROR, message=message, data=None)


def unauth_error(message=""):
    return restful_result(code=HttpCode.UNAUTH_ERROR, message=message, data=None)


def forbidden_error(message=""):
    return restful_result(code=HttpCode.FORBIDDEN_ERROR, message=message, data=None)


def internal_server_error(message=""):
    return restful_result(code=HttpCode.INTERNAL_SERVER_ERROR, message=message, data=None)

"""
