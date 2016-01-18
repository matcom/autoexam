# -*- coding: utf8 -*-
from __future__ import print_function

import gen
import sys


def test_no_repeated_questions():
    print("Checking no repeated questions ", end='')

    for i in range(10000):
        test = gen.generate_quiz()
        used_questions = set()

        if i % 500 == 0:
            print(".", end='')
            sys.stdout.flush()

        for q in test:
            if q.number in used_questions:
                print(u" (!) Repeated question: {0}".format(q))
                return

            used_questions.add(q.number)

    print(" OK")


def test_suite():
    gen.parser()
    test_no_repeated_questions()


if __name__ == '__main__':
    test_suite()
