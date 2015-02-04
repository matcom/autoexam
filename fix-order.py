import gen
import sys
import argparse
import os
import json


def main():
	parser = argparse.ArgumentParser(description="Rebuilds the Order.txt file fixing each questions order list.")
	parser.add_argument('order', help='The original (screwed-up) Order.txt file.')
	parser.add_argument('master', help='The original Master.txt file.')
	parser.add_argument('src', help='The folder with all the Text-*.tex files.')

	args = parser.parse_args()

	fix(args)


def fix(args):
	gen.parser(args)
	questions = gen.questions_by_id

	with open(args.order) as fp:
		order = json.load(fp)

	for f in os.listdir(args.src):
		if f.startswith('Test-'):
			try:
				test_id = f[5:-4]
				fix_test(args.src, f, test_id, questions, order)
			except Exception as e:
				sys.stderr.write("ERROR: %s \t (%s)\n" % (test_id, repr(e)))

	s = json.dumps(order)
	print(s)


def fix_test(src, f, test_id, questions, order):
	test_order = order[test_id]
	tex_file = open(os.path.join(src, f))

	lines = tex_file.readlines()

	test_questions = list(test_order['questions'])

	while lines:
		l = lines.pop(0).strip()
		if l.startswith('\\item'):
			question_meta = test_questions.pop(0)
			question = questions[question_meta['id']]
			order = []

			while lines:
				li = lines.pop(0).strip()
				if li.startswith('\\item'):
					li = li.decode('utf8')[5:].strip()

					for i, (_, _, opt) in enumerate(question.options):
						opt = opt.split('\n')[0].strip()
						if li == opt.strip():
							order.append(i)
							break

				elif li.startswith('\\end{enumerate}'):
					if len(order) != len(question.options) or len(set(order)) != len(question.options):
						print(order)

					question_meta['order'] = order
					answers = []

					for i in question_meta['visual_answers']:
						answers.append(order[i - 1])

					question_meta['answers'] = answers

					break


if __name__ == '__main__':
	main()
