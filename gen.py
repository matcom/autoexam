#! /usr/bin/python
#-*-coding: utf8-*-

import os.path
import collections
import jinja2
import random
import qrcode
import os
import sys
import pprint
import json
import scanresults
import argparse


database = collections.defaultdict(lambda: [])
questions_by_id = {}
restrictions = {}
restrictions_order = {}
test_id = 1
debug = sys.argv.count('-d')
count = 0

VERSION = 1


def preprocess_line(line, remove_comments=True):
    if debug > 1:
        print(u'Reading line: "%s"' % line.decode('utf8'))

    line = line.strip().decode('utf8')
    if remove_comments and '%' in line:
        idx = line.index('%')
        if idx >= 0 and (idx == 0 or line[idx-1] != '\\'):
            line = line[:idx].strip()

    if debug > 1:
        print(u'Returning line: "%s"' % line)

    return line


def parser(master_path):
    """
    Lee el archivo master y se parsea cada una de las preguntas.
    """
    master = open(master_path)
    lines = master.readlines()
    master.close()

    # Parse the header
    i = 0
    while i < len(lines):
        l = preprocess_line(lines[i][:-1])
        i += 1
        if l:
            if l.startswith('-'):
                break
            tag, value = l.split(':')
            tag = tag.strip()
            value = int(value.strip())
            restrictions[tag] = value
            restrictions_order[tag] = len(restrictions_order)

            if debug:
                print('Adding restriction: %s: %i' % (tag, value))

    if not 'total' in restrictions:
        raise ValueError('Missing `total` directive')

    if debug:
        print('Restrictions:')
        pprint.pprint(restrictions)

    # Parse questions
    while i < len(lines):
        i = parse_question(i, lines)


def parse_question(i, lines):
    """Crea el objeto pregunta y la agrega en los contenidos
    que se evalúan en la misma."""

    global count

    # Find the id line
    i, identifier = parse_id(i, lines)
    i, tags = parse_tag(i, lines)
    i, header = parse_header(i, lines)
    i, answers = parse_answers(i, lines)

    count += 1
    question = Question(header, answers, count, tags)

    # Add answers to given tags
    for t in tags:
        database[t].append(question)

    questions_by_id[count] = question

    return i


def parse_header(i, lines):
    header = u""

    while i < len(lines):
        l = preprocess_line(lines[i][:-1], remove_comments=False)
        if l and l[0] == '_':
            break
        header += l + '\n'
        i += 1

    header = header.strip()

    if not header:
        raise ValueError('Header not found at line %i' % i)

    if debug:
        print(u'Found header: \n%s' % header)

    return i, header


def strip(line):
    lines = list(reversed(line.split('\n')))
    i = 0

    while i < len(lines):
        l = lines[i].strip()
        if l and not l.startswith('%'):
            break
        i += 1

    if i >= len(lines):
        return None

    return u'\n'.join(reversed(lines[i:]))


def parse_answer(i, lines):
    answer = u""

    while i < len(lines):
        l = preprocess_line(lines[i][:-1], remove_comments=False)
        if l and ((answer and l[0] == '_') or l[0] == '('):
            break
        answer += l + '\n'
        i += 1

    if not answer:
        return i, None

    answer = strip(answer)

    if answer.lower().startswith('_*'):
        answer = (False, True, answer[2:].strip())
    elif answer.lower().startswith('_x*'):
        answer = (True, True, answer[3:].strip())
    elif answer.lower().startswith('_x'):
        answer = (True, False, answer[2:].strip())
    elif answer.lower().startswith('_'):
        answer = (False, False, answer[1:].strip())
    else:
        raise ValueError(u'Invalid answer prefix in "%s" at line %i' %
                        (answer, i))

    if debug:
        print(u'Found answer:\n%s' % str(answer))

    return i, answer


def parse_answers(i, lines):
    answers = []

    while i < len(lines):
        i, answer = parse_answer(i, lines)
        if answer:
            answers.append(answer)
        else:
            break

    if not answers:
        raise ValueError('No answer found at line %i' % i)

    return i, answers


def parse_tag(i, lines):
    i, l = skip_blank(i, lines)

    if l is None:
        raise ValueError('Tag line not found')

    tags = l.split()

    for t in tags:
        if t[0] != '@':
            raise ValueError('Invalid tag %s' % t)
        if debug:
            print(u'Found tag: %s' % t)

    return i, tags


def skip_blank(i, lines):
    while i < len(lines):
        l = preprocess_line(lines[i][:-1])
        if l:
            return i+1, l
        i += 1

    return i, None


def parse_id(i, lines):
    i, l = skip_blank(i, lines)

    if l is None:
        raise ValueError('Id line not found')

    if l[0] != '(' or l[-1] != ')':
        raise ValueError(u'Not valid Id line: %s at line %i' % (l, i))

    id_text = l[1:-1]

    if debug:
        print(u'Found identifier: %s' % id_text)

    return i, id_text


class Question:
    """Las preguntas tienen un campo `header` que es el enunciado,
    y opciones. Algunas de estas opciones pueden considerarse
    respuestas correctas."""

    def __init__(self, header, options, number, tags, options_id=None, fixed=None):
        if (not header or not options):
            raise ValueError(u'Invalid question %s' % number)

        self.options = options
        self.header = header
        self.number = number
        self.tags = tags
        self.fixed = fixed or {}
        self.options_id = options_id

        if self.options_id is None:
            self.options_id = {}

            for i, o in enumerate(self.options):
                self.options_id[o] = i
                if o[1]:
                    self.fixed[o] = i

    @property
    def correct_answers(self):
        return len([None for r, f, o in self.options if r])

    @property
    def answers_count(self):
        return len(self.options)

    def enumerate_options(self):
        return enumerate(self.options)

    def shuffle(self):
        """
        Devuelve las opciones desordenadas.
        """
        options = list(self.options)
        random.shuffle(options)

        for o in list(options):
            if o in self.fixed:
                pos = self.fixed[o]
                idx = options.index(o)
                tmp = options[pos]
                options[pos] = o
                options[idx] = tmp

        return Question(self.header, options, self.number, self.tags, self.options_id, self.fixed)

    def convert(self):
        order = [self.options_id[o] for o in self.options]

        print(order)

        return scanresults.Question(self.number, len(self.options),
                                    self.multiple, order=order)

    @property
    def multiple(self):
        return len([o for o in self.options if o[0]]) > 1

    def options_text(self, i, max):
        alphabet = list("abcdefghijklmnopqrstuvwxyz")
        first = True

        for a, o in zip(alphabet, self.options):
            if first:
                yield i, a
                first = False
            else:
                yield "", a

        for i in range(len(self.options), max):
            yield "", ""

    def __str__(self):
        return str(self.number)

    def qrcode(self):
        opts = "(%s)" % ",".join(str(self.options_id[o])
                                 for o in self.options)
        # return str(self.number) + '**'

        if self.multiple:
            return"%i*%s" % (self.number, opts)
        else:
            return "%i%s" % (self.number, opts)


def qrcode_data(test_id, i, test):
    return "%i|%i|%i" % (test_id, i, VERSION)


def generate_qrcode(i, test):
    filename = 'generated/v{0}/qrcode-{1}.png'.format(test_id, i)

    f = open(filename, 'w')
    qr = qrcode.QRCode(box_size=10, border=0)
    data = qrcode_data(test_id, i, test)
    qr.add_data(data)

    if debug > 1:
        print('QR Code data: %s' % data)
    if debug > 2:
        qr.print_tty()

    qr.make()
    img = qr.make_image()
    img.save(f)
    f.close()


def generate_quiz(args=None):
    total = restrictions['total']
    res = dict(restrictions)
    res.pop('total')
    base = {}

    for k, v in database.items():
        base[k] = list(v)

    test = set()
    tries = 0

    def get_question(tag):
        if tag not in base:
            raise ValueError('Could not fullfill a restriction '
                             'with tag "%s"' % tag)
        i = random.choice(range(len(base[tag])))
        q = base[tag].pop(i)

        if not base[tag]:
            base.pop(tag)

        if args and not args.dont_shuffle_options:
            q = q.shuffle()

        if debug > 1:
            print(u'Selection question:\n%s' % str(q))

        return q

    while len(test) < total and tries < 10 * total:
        if res:
            tag = random.choice(res.keys())
            q = get_question(tag)
            res[tag] -= 1
            if not res[tag]:
                res.pop(tag)
        else:
            tag = random.choice(base.keys())
            q = get_question(tag)

        test.add(q)

    if len(test) < total:
        raise ValueError('Could not complete test')

    test = list(test)
    random.shuffle(test)

    if args and args.dont_shuffle_tags:
        test.sort(key=lambda q: restrictions_order[q.tags[0]])

    if args and args.sort_questions:
        test.sort(key=lambda q: q.number)

    return test


def generate(n, args):
    # Guaranteeing reproducibility
    seed = args.seed or random.randint(1, 2 ** 32)
    random.seed(seed)

    text_template = jinja2.Template(open(args.text_template).
                                    read().decode('utf8'))
    answer_template = jinja2.Template(open(args.answer_template).
                                      read().decode('utf8'))
    sol_template = jinja2.Template(open('templates/solution_template.txt').
                                   read().decode('utf8'))
    master_template = jinja2.Template(open(args.master_template).
                                      read().decode('utf8'))

    questions = set()
    for qs in database.values():
        for q in qs:
            questions.add(q)

    questions = sorted(questions, key=lambda q: q.number)

    if not args.dont_generate_master:
        master_file = open('generated/v{0}/Master.tex'.format(test_id), 'w')
        master_file.write(master_template.render(test=questions,
                          header=args.title).encode('utf8'))
        master_file.close()

    sol_file = open('generated/v{0}/grader.txt'.format(test_id), 'w')
    sol_file.write(sol_template.render(test=questions,
                   test_id=test_id, questions_value=args.questions_value).encode('utf8'))
    sol_file.close()

    order = {}

    answers = []

    for i in range(n):
        if debug:
            print('Generating quiz number %i' % i)

        test = generate_quiz(args)
        # order[i] = dict(exam_id=test_id, id=i, options=[])
        order[i] = scanresults.Test(test_id, i, [q.convert() for q in test])
        generate_qrcode(i, test)

        if not args.dont_generate_text:
            text_file = open('generated/v{0}/Test-{1:04}.tex'.format(test_id, i), 'w')

            text_file.write(text_template.render(
                            test=test, number=i, header=args.title).encode('utf8'))
            text_file.close()

        answers.append(dict(test=list(enumerate(test)), number=i, seed=seed, max=max(len(q.options) for q in test)))

        if len(answers) == args.answers_per_page or i == n - 1:
            answer_file = open('generated/v{0}/Answer-{1:04}.tex'.format(test_id, i / args.answers_per_page), 'w')
            answer_file.write(answer_template.render(answers=answers).encode('utf8'))
            answer_file.close()
            answers = []

    scanresults.dump(order, 'generated/v{0}/order.json'.format(test_id))

    with open('generated/v{0}/seed'.format(test_id), 'w') as fp:
        fp.write(str(seed) + '\n')


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description="Parses a master file and generates tests.")
    args_parser.add_argument('master', metavar="PATH", help="Path to the master file that contains the test description.")
    args_parser.add_argument('-c', '--tests-count', metavar='N', help="Number of actual tests to generate. If not supplied, only the master file will be generated.", type=int, default=0)
    args_parser.add_argument('-a', '--answers-per-page', help="Number of answer sections to generate per page. By default is 1. It is up to you to ensure all them fit right in your template.", metavar='N', type=int, default=1)
    args_parser.add_argument('-t', '--title', help="Title of the test.", default="")
    args_parser.add_argument('--answer-template', help="Template for the answers sheets.", default="latex/answer_template.tex")
    args_parser.add_argument('--master-template', help="Template for the master sheet.", default="latex/master_template.tex")
    args_parser.add_argument('--text-template', help="Template for the text sheets.", default="latex/text_template.tex")
    args_parser.add_argument('-v', '--questions-value', help="Default value for each question.", metavar='N', type=float, default=1.)
    args_parser.add_argument('--dont-shuffle-tags', help="Disallow shuffling of tags.", action='store_true')
    args_parser.add_argument('--sort-questions', help="After selecting questions, put them in the same order as in the master.", action='store_true')
    args_parser.add_argument('--dont-shuffle-options', help="Do not shuffle the options in the questions.", action='store_true')
    args_parser.add_argument('--dont-generate-text', help="Do not generate text sheets, only answers.", action='store_true')
    args_parser.add_argument('--election', help="Toggle all options for election mode.", action='store_true')
    args_parser.add_argument('--questionnaire', help="Toggle all options for questionnaire mode.", action='store_true')
    args_parser.add_argument('--dont-generate-master', help="Do not generate a master file.", action='store_true')

    args = args_parser.parse_args()

    if args.election:
        args.answer_template = 'latex/election_template.tex'
        args.sort_questions = True
        args.dont_shuffle_options = True
        args.dont_generate_text = True
        args.dont_generate_master = True

    if args.questionnaire:
        args.answer_template = 'latex/questionnaire_template.tex'
        args.sort_questions = True
        args.dont_shuffle_options = True
        args.dont_generate_text = True
        args.dont_generate_master = True

    if not os.path.exists('generated'):
        os.mkdir('generated')

    for d in os.listdir('generated'):
        num = int(d[1:])
        if num >= test_id:
            test_id = num + 1

    os.mkdir('generated/v{0}'.format(test_id))

    parser(master_path)
    generate(args.tests_count, args)

    print('Generated v{0}'.format(test_id))
