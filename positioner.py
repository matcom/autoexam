import json
import argparse
import os


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('version', help='The `v#` folder where your generated pdfs are.')

	args = parser.parse_args()

	base_path = os.path.join('generated', args.version)

	with open(os.path.join(base_path, 'Order.txt')) as fp:
		orders = json.load(fp)

	for f in os.listdir(base_path):
		if f.startswith('Answer-') and f.endswith('.log'):
			test_id = f.strip('Answer-').strip('.log')
			with open(os.path.join(base_path, f)) as fp:
				positions = parse(fp, orders)
				orders[test_id]['positions'] = positions

	with open(os.path.join(base_path, 'Order.txt'), 'w') as fp:
		json.dump(orders, fp, indent=4)


def get_description(line):
	line = line.split()
	return line[1].strip('()')


def get_position(line):
	line = line.split()
	x, y = line[2].strip('()').split(',')
	return (int(x), int(y))


def parse(fp, orders):
	ticks = []

	for line in fp:
		line = line.strip()

		if line.startswith('[UPPER-LEFT]'):
			upper_left = get_position(line)
		elif line.startswith('[UPPER-RIGHT]'):
			upper_right = get_position(line)
		elif line.startswith('[BOTTOM-LEFT]'):
			bottom_left = get_position(line)
		elif line.startswith('[BOTTOM-RIGHT]'):
			bottom_right = get_position(line)
		elif line.startswith('[TICK-POSITION]'):
			ticks.append(dict(description=get_description(line), position=get_position(line)))

	return dict(upper_left=upper_left,
				upper_right=upper_right,
				bottom_left=bottom_left,
				bottom_right=bottom_right,
				ticks=ticks)

if __name__ == '__main__':
	main()
