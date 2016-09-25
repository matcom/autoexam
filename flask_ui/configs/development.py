from os import environ as env
from os.path import abspath, dirname, join

basedir = abspath(dirname(__file__))

SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + join(basedir, 'flask_ui.db')
SQLALCHEMY_MIGRATE_REPO = join(basedir, 'migrations')