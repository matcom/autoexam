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

	all_sum = 0

	if os.path.exists(app.data_file):
		with open(app.data_file) as fp:
			data = json.load(fp)

			if app.all is not None:
				all_sum = data['1']['options'][str(app.all)]

	for i,n in enumerate(app.names):
		if data is not None:
			people.append(dict(name=n, votes=data['1']['options'][str(i)] + all_sum))
		else:
			people.append(dict(name=n, votes=0))

	if os.path.exists(app.extra):
		with open(app.extra) as fp:
			for l in fp:
				l = l.strip().split()

				if len(l) > 1:
					name, votes = " ".join(l[:-1]), int(l[-1])
					people.append(dict(name=name, votes=votes))

	return jsonify(people=people)


def run(args):
	app.data_file = os.path.abspath(args.data)
	app.all = args.all
	app.extra = os.path.abspath(args.extra)
	app.names = [s.strip() for s in open(args.names).readlines() if s.strip()]
	app.run(host=args.host, port=args.port, debug=args.debug)
