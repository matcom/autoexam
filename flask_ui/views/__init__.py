from flask_ui import app, db
from flask_ui.models import User


@app.route('/')
def init():
    return '<h1>Welcome to Autoexam</h1>'


@app.route('/users')
def users():
    return '%r' % dir(User.query)
