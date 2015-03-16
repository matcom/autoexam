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
	people = []
	data = None

	if os.path.exists(app.data_file):
		with open(app.data_file) as fp:
			data = json.load(fp)

	for i,n in enumerate(app.names):
		if data is not None:
			people.append(dict(name=n, votes=data['1']['options'][str(i)]))
		else:
			people.append(dict(name=n, votes=0))

	return jsonify(people=people)


def run(args):
	app.data_file = os.path.abspath(args.data)
	app.names = [s.strip() for s in open(args.names).readlines() if s.strip()]
	app.run(host=args.host, port=args.port, debug=args.debug)
