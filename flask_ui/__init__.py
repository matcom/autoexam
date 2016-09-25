from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('configs/development.py')
db = SQLAlchemy(app)

def run(args):
    from flask_ui import views, models

    app.run(host=args.host, port=args.port, debug=args.debug)
