import os
import json

from flask import Flask
from flask import send_file, jsonify

app = Flask(__name__)


@app.route('/')
def page():
	return send_file('webpoll.html')


@app.route('/data/')
def data():
	with open(app.data_file) as fp:
		data = json.load(fp)

	people = []

	for i,n in enumerate(app.names):
		people.append(dict(name=n, votes=data['1']['options'][str(i)]))

	return jsonify(people=people)


def run(args):
	app.data_file = os.path.abspath(args.data)
	app.names = [s.strip() for s in open(args.names).readlines() if s.strip()]
	app.run(host=args.host, port=args.port, debug=args.debug)
