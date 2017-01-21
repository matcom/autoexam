#! /usr/bin/python
#-*-coding: utf8-*-

import os.path
import collections
import jinja2
import random
import qrcode
import os
import pprint
import sys
import pprint
import json
import scanresults
import csv
import argparse
import json


database = collections.defaultdict(lambda: [])
questions_by_id = {}
restrictions = {}
restrictions_order = {}
test_id = 1
debug = sys.argv.count('-d')
count = 0
names = {}
rules = []
solutions = {}

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


def parser(master_path="master.txt"):
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

    # Parse names
    if os.path.exists("names.csv"):
        all_names = list(csv.reader(open("names.csv")))
        fields = all_names[0][1:]
        all_names = all_names[1:]

        for line in all_names:
            name = line[0].decode('utf8')
            names[name] = {}

            for field, val in zip(fields, line[1:]):
                names[name][field] = float(val) if val else 0.0


    if os.path.exists("rules.txt"):
        with open('rules.txt') as fp:
            for line in fp:
                line = line.strip()
                if not line:
                    continue

                splitted = line.split("=>")

                if len(splitted) != 2:
                    raise ValueError(u"Error parsing rule {0}".format(line))

                pre, post = splitted
                pre = pre.strip().split()
                post = post.strip().split()

                if len(pre) % 3 != 0:
                    raise ValueError(u"Error parsing precondition for rule {0}".format(line))

                if len(post) % 2 != 0:
                    raise ValueError(u"Error parsing postcondition for rule {0}".format(line))

                rule = []

                for i in range(len(pre) / 3):
                    key, comp, val = pre[3*i:3*i+3]
                    key = key.strip()
                    comp = comp.strip()
                    val = float(val.strip())

                    if comp in rules_functors:
                        rule_item = rules_functors[comp](key, val)
                    else:
                        raise ValueError(u"Error parsing comparison symbol {0} for rule {1}".format(val, line))

                    rule.append(rule_item)

                action = []

                for i in range(len(post) / 2):
                    tag, val = post[2*i:2*i+2]
                    tag = tag.strip()
                    val = int(val.strip())

                    action.append((tag, val))

                rules.append((rule, action))


def less_than_rule(key, val):
    def test(results):
        actual = results.get(key)
        return actual is not None and actual < val
    return test


def less_equal_than__rule(key, val):
    def test(results):
        actual = results.get(key)
        return actual is not None and actual <= val
    return test


def greater_than_rule(key, val):
    def test(results):
        actual = results.get(key)
        return actual is not None and actual > val
    return test


def greater_equal_than_rule(key, val):
    def test(results):
        actual = results.get(key)
        return actual is not None and actual >= val
    return test


def equal_than_rule(key, val):
    def test(results):
        actual = results.get(key)
        return actual is not None and actual == val
    return test


rules_functors = {
    '<': less_than_rule,
    '<=': less_equal_than__rule,
    '>': greater_than_rule,
    '>=': greater_equal_than_rule,
    '=': equal_than_rule,
    '==': equal_than_rule,
}


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
    solutions[count] = [idx for idx,a in enumerate(answers) if a[0]]

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

    # if not answers:
        # raise ValueError('No answer found at line %i' % i)

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
        if (not header):
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
                if o in self.options_id:
                    raise Exception('Invalid option exception. Duplicated answers are not allowed')
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

    	if debug:
            print(order)

        return scanresults.Question(self.number, len(self.options),
                                    self.multiple, order=order)

    @property
    def multiple(self):
        return len([o for o in self.options if o[0]]) > 1

    def __eq__(self, other):
        return self.number == other.number

    def __hash__(self):
        return hash(self.number)

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


def qrcode_data(test_id, i, test, page):
    return "%i|%i|%i|%i" % (test_id, i, page, VERSION)


def generate_qrcode(i, test, page):
    filename = 'generated/v{0}/qrcode-{1}-{2}.png'.format(test_id, i, page)

    f = open(filename, 'w')
    qr = qrcode.QRCode(box_size=10, border=0)
    data = qrcode_data(test_id, i, test, page)
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
        tries += 1

    if len(test) < total or res:
        raise ValueError('Could not complete test')

    test = list(test)
    random.shuffle(test)

    if args and args.dont_shuffle_tags:
        test.sort(key=lambda q: restrictions_order[q.tags[0]])

    if args and args.sort_questions:
        test.sort(key=lambda q: q.number)

    # Moving manual questions to the end
    test.sort(key=lambda q: '@autoexam-manual' in q.tags)

    return test


def generate(n, args):
    # Guaranteeing reproducibility
    seed = args.seed or random.randint(1, 2 ** 32)
    random.seed(seed)

    n += len(names)
    names_text = sorted(names.keys())

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
    order['answers_per_page'] = args.answers_per_page
    order['seed'] = seed

    answers = []
    texts = []

    for i in range(n):
        if debug:
            print('Generating quiz number %i' % i)

        name = names_text[i] if i < len(names_text) else ""
        test = generate_quiz(args)
        results = names.get(name)


        if results is not None:
            for rule in rules:
                matches = True

                tests, actions = rule

                for t in tests:
                    matches = matches and t(results)

                if matches:
                    for action in actions:
                        print(u"Applying {0} to {1}".format(action, name).encode("utf8"))

                        tag, val = action
                        possible_questions = [q for q in test if tag in q.tags]

                        print(u" There are %i possible questions to select" % len(possible_questions))

                        if val < 0:
                            to_remove = random.sample(possible_questions, min(-val, len(possible_questions)))
                            print(u" Selected %i questions to remove" % len(to_remove))

                            for q in to_remove:
                                test.remove(q)

                            print(u" Test has %i questions remaining" % len(test))
                        else:
                            raise ValueError(u"Adding questions is not yet allowed.")


        order[i] = scanresults.Test(test_id, i, [q.convert() for q in test]).to_dict()
        texts.append(dict(test=test, number=i, header=args.title, name=name))

        page = 1
        answers_in_page = []

        for k,q in enumerate(test):
            if '@autoexam-manual' not in q.tags:
                answers_in_page.append((k, q))

            if len(answers_in_page) == args.answers_per_page or (k == len(test) - 1 and answers_in_page):
                generate_qrcode(i, test, page)
                answers.append(dict(test=answers_in_page, number=i, page=page, name=name, seed=seed, max=max(len(q.options) for q in test)))
                answers_in_page = []
                page += 1

    order['total_tests'] = len(texts)
    order['total_answers'] = len(answers)

    if not args.dont_generate_text:
        with open('generated/v{0}/Tests.tex'.format(test_id), 'w') as text_file:
            text_file.write(text_template.render(tests=texts).encode('utf8'))

    with open('generated/v{0}/Answers.tex'.format(test_id), 'w') as answer_file:
        answer_file.write(answer_template.render(answers=answers).encode('utf8'))

    with open('generated/v{0}/order.json'.format(test_id), 'w') as fp:
        json.dump(order, fp, indent=4)

    with open('generated/v{0}/seed'.format(test_id), 'w') as fp:
        fp.write(str(seed) + '\n')
