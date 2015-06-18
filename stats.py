from __future__ import print_function

import sys
import collections
import gen
import math
import random


def mean_and_stdev(samples):
	mean = sum(samples) * 1.0 / len(samples)
	var = sum((x - mean) ** 2 for x in samples)
	stdev = math.sqrt(var)

	return mean, stdev


def build_stats(args):
	gen.parser()

	print('Running %i simulations' % (args.samples))

	questions_distribution = collections.defaultdict(lambda: 0)
	tags_distribution = {t:[] for t in gen.database}
	grades_distribution = collections.defaultdict(lambda: 0)

	for i in range(args.samples):
		if i % 1000 == 0:
			print('.', end='')
			sys.stdout.flush()

		test = gen.generate_quiz()

		tags = collections.defaultdict(lambda: 0)

		for q in test:
			questions_distribution[q.number] += 1
			for t in q.tags:
				tags[t] += 1

		for t, v in tags.items():
			tags_distribution[t].append(v)

		chance = 0.0

		while chance <= 1:
			pass
			chance += args.grades_scale


	print("\nQuestions distribution\n------------------------\nNo.\tAppeareances (%)\n------------------------")

	for i,v in questions_distribution.items():
		p = v * 1.0 / args.samples
		print("%i\t%.2f" % (i, p * 100))

	print("\nTags distribution\n------------------------\nTag\tTimes per test\n------------------------")

	for i,v in tags_distribution.items():
		m, s = mean_and_stdev(v)
		print("%s\t%.2f" % (i, m))
