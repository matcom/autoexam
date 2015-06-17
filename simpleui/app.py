import os

from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/vote/')
def create_vote():
	return render_template('vote.html')


def run(args):
	app.run(host=args.host, port=args.port, debug=args.debug)
