import os

from flask import Flask
from flask import send_file

app = Flask(__name__)


@app.route('/')
def page():
	return send_file('webpoll.html')


@app.route('/data/')
def data():
	return send_file(app.data_file)


def run(args):
	app.data_file = os.path.abspath(args.data)
	app.run(host=args.host, port=args.port, debug=args.debug)
