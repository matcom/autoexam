#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import sys
import argparse
import shutil
import json
import gen
import evaluator as ev
# import webpoll.webpoll as wp
# import simpleui.app as sui

from tabulate import tabulate
from stats import build_stats

autoexam_source = os.path.dirname(os.path.realpath(__file__))


def src(p):
    return os.path.join(autoexam_source, p)


def check_project_folder():
    if is_project_folder():
        return True

    error("You need to be in the root of an Autoexam project folder to do this.")
    return False


def is_project_folder():
    return os.path.exists('.autoexam')


def generate(args):
    if not check_project_folder():
        return

    if args.election or get_project_option('election', bool):
        args.answer_template = 'templates/election_template.tex'
        args.sort_questions = True
        # args.dont_shuffle_options = True
        args.dont_generate_text = True
        args.dont_generate_master = True

    if args.questionnaire or get_project_option('questionnaire', bool):
        args.answer_template = 'templates/questionnaire_template.tex'
        args.sort_questions = True
        args.dont_shuffle_options = True
        args.dont_generate_text = True
        args.dont_generate_master = True

    name = get_project_option('name')
    test_id = int(get_project_option('next_version'))

    print("Generating project `{0}`".format(name))

    gen.test_id = test_id
    set_project_option('next_version', test_id + 1)

    os.mkdir(os.path.join('generated', 'v{0}'.format(test_id)))

    gen.parser()
    gen.generate(args.tests_count, args)

    print("Compiling LaTeX source files")

    gen_folder = os.path.join('generated', 'v' + str(test_id))

    def dst(path):
        return os.path.join(gen_folder, path)

    os.chdir(gen_folder)

    for f in os.listdir('.'):
        if f.endswith('.tex'):
            os.system("pdflatex %s -interaction=nonstopmode > compile_latex.log" % f)

    os.mkdir('pdf')
    os.mkdir('src')
    os.mkdir('log')

    for f in os.listdir('.'):
        if f.endswith('.pdf'):
            shutil.move(f, 'pdf')
        elif f.endswith('.log'):
            shutil.move(f, 'log')
        elif f.endswith('.tex') or f.endswith('.png'):
            shutil.move(f, 'src')
        elif f.endswith('.aux'):
            os.remove(f)

    os.chdir('..')

    if os.path.exists('last'):
        os.remove('last')

    os.symlink('v' + str(test_id), 'last')

    print("Test generated successfully")


def init(args):
    if is_project_folder():
        error("This project is already initialized.\nPlease run this outside this folder.")
        return

    folder = args.folder or args.name

    if os.path.exists(folder):
        error("Folder `{0}` already exists.".format(folder))
        return

    folder = os.path.abspath(folder)

    def dst(p):
        return os.path.join(folder, p)

    print("Creating folder `{0}`".format(folder))
    os.mkdir(folder)

    print("Creating project skeleton.")
    open(dst('.gitkeep'), 'w').close()

    shutil.copytree(src('latex'), dst('templates'))
    shutil.copy(src('example-config.conf'), dst('config.conf'))

    if args.election:
        shutil.copy(src('example-election.txt'), dst('master.txt'))
    else:
        shutil.copy(src('example-master.txt'), dst('master.txt'))

    os.mkdir(dst('generated'))
    open(dst('generated/.gitkeep'), 'w').close()

    os.mkdir(dst('.autoexam'))
    os.chdir(folder)

    set_project_option('name', args.name)
    set_project_option('next_version', '1')

    if args.election:
        set_project_option('election', True)

    if args.questionnaire:
        set_project_option('questionnaire', True)


def set_project_option(option, value):
    f = open(os.path.join('.autoexam', option), 'w')
    f.write(str(value))
    f.write('\n')
    f.close()


def get_project_option(option, type_builder=str):
    try:
        with open(os.path.join('.autoexam', option), 'r') as fp:
            return type_builder(fp.readline().strip())
    except:
        return None


def status(args):
    if not check_project_folder():
        return

    name = get_project_option('name')
    print("General project status:")
    print("  Name: {0}".format(name))

    if (args.generation):
        print('\nGeneration status:')
        print('  Next automatic version: {0}'.format(get_project_option('next_version')))


def edit(args):
    if not check_project_folder():
        return

    if args.file == "master":
        os.system("edit master.txt")


def error(msg):
    print('')

    for line in msg.split('\n'):
        print(" (!) ERROR: " + line)

    print('')


def warn(msg):
    print('')

    for line in msg.split('\n'):
        print(" (!) WARNING: " + line)

    print('')


def stats(args):
    if not check_project_folder():
        return

    build_stats(args)


def webpoll(args):
    wp.run(args)


def simpleui(args):
    sui.run(args)


def report(args):
    if not check_project_folder():
        return

    base_path = get_base_path(args)
    result_path = os.path.join(base_path, 'results.json')
    order_path = os.path.join(base_path, 'order.json')

    columns = ['Id']

    if not os.path.exists(result_path):
        error("No `results.json` file found. Maybe the test hasn't been graded yet?")
        return

    with open(result_path) as fp:
        results = json.load(fp)

    if not 'grades' in results:
        error("The file `results.json` contains no grading data. Was the test evaluated with a valid `grader.txt` sheet?")
        return

    if not os.path.exists(order_path):
        error("No `order.json` file found. Is this a correctly generated test?")
        return

    with open(order_path) as fp:
        orders = json.load(fp)

    question_ids = set()

    for _, exam in orders.items():
        for q in exam['questions']:
            question_ids.add(q['id'])

    names = {}

    if os.path.exists("names.txt"):
        columns.append("Name")

        with open("names.txt", 'r') as fp:
            for line in fp:
                line = line.decode("utf8").strip().split()
                tid = line[0]
                name = " ".join(l for l in line[1:])
                names[tid] = name

    if 'grades' in args.data:
        columns.append('Grade')

    if 'partials' in args.data:
        for i in question_ids:
            columns.append('P{0}'.format(i))

    if 'selection' in args.data:
        for i in question_ids:
            columns.append('S{0}'.format(i))

    rows = []

    for i, d in sorted(results['grades'].items(), key=lambda x: int(x[0])):
        data = [i]

        if names:
            data.append(names[i])

        if 'grades' in args.data:
            data.append(d['total_grade'])

        if 'partials' in args.data:
            for qid in question_ids:
                if str(qid) in d['questions_grades']:
                    data.append(d['questions_grades'][str(qid)])
                else:
                    data.append(None)

        if 'selection' in args.data:
            questions = {q['id']: q for q in orders[i]['questions']}

            for qid in question_ids:
                if qid in questions:
                    data.append(", ".join(str(i+1) for i in sorted(questions[qid]['answers'])))
                else:
                    data.append(None)

        rows.append(data)

    print(tabulate(rows, headers=columns, tablefmt=args.format))


def get_base_path(args):
    if args.version:
        return os.path.join('generated', str(args.version))
    else:
        return os.path.join('generated', 'last')


def grade(args):
    if not check_project_folder():
        return

    base_path = get_base_path(args)
    grader_path = os.path.join(base_path, 'grader.txt')
    order_path = os.path.join(base_path, 'order.json')
    result_path = os.path.join(base_path, 'results.json')

    if os.path.exists(result_path) and not args.force:
        error('Test already evaluated. Pass --force to ovewrite.')
        return

    if not os.path.exists(order_path):
        error('No order.json file found. Cannot evaluate.')
        return

    if os.path.exists(grader_path):
        grades = ev.evaluate(grader_path, order_path)
    else:
        warn('No grader.txt sheet was found. Will only generate stats.')
        grades = None

    stats = ev.get_stats(order_path)

    with open(result_path, 'w') as fp:
        json.dump({"grades": grades, "stats": stats}, fp, indent=4)


def review(args):
    if not check_project_folder():
        return

    base_path = get_base_path(args)
    result_path = os.path.join(base_path, 'results.json')

    if not os.path.exists(result_path):
        error("Test hasn't been scanned yet")
        return

    with open(result_path, 'r') as fp:
        results = json.load(fp)

    tests_with_warnings = {}

    for test, data in results.items():
        if data.get("warnings"):
            warnings = []

            for w in data["warnings"]:
                if w["type"] != "Multiple Selection":
                    warnings.append(w)

            if warnings:
                tests_with_warnings[test] = warnings

    for test in sorted(tests_with_warnings, key=int):
        print("Test No. {0}".format(test))
        warnings = tests_with_warnings[test]

        for w in warnings:
            print("  Question {0}".format(w["question"]))
            print("    " + w["message"])
            print("    Scanned selection: " + ", ".join(str(q) for q in results[test]["questions"][w["question"]-1]["visual_answers"]))
            answer = raw_input("    If this information correct? [Y/n]: ")

            while answer.lower() not in ["", "y", "n"]:
                answer = raw_input("    Please answer yes (y) or no (n). Is this information correct? [Y/n]: ")

            if answer.lower() == "n":
                need_check = True

                while need_check:
                    correct_answer = raw_input("    Enter the correct selection (numbers separated by spaces only):")
                    try:
                        correct_answer = [int(s) for s in correct_answer.split()]
                        print("    Modified selection: " + ", ".join(str(q) for q in correct_answer))

                        answer = raw_input("    If this new modification correct? [Y/n]: ")

                        while answer.lower() not in ["", "y", "n"]:
                            answer = raw_input("    Please answer yes (y) or no (n). Is this new modification correct? [Y/n]: ")

                        if answer != "n":
                            need_check = False

                            question_order = results[test]["questions"][w["question"]-1]["order"]
                            correct_order = [question_order[i-1] for i in correct_answer]

                            question = results[test]["questions"][w["question"]-1]
                            question["visual_answers"] = correct_answer
                            question["answers"] = correct_order
                    except:
                        print("    Error parsing your response. Please answer again.")
        print("")

    
    answer = raw_input("Apply all modifications? [yes/N]: ")

    if answer == "yes":
        shutil.copy(result_path, result_path + ".backup")
        with open(result_path, "w") as fp:
            json.dump(results, fp, indent=4, sort_keys=True)
        print("Changes saved. Original result file kept with .backup extension.")
    else:
        print("No actual changes were saved. Original result file unmodified.")

def main():
    if 'autoexam.py' in os.listdir('.'):
        error("Please don't run this from inside the Autoexam source folder.\nThis is an evil thing to do that will break the program.")
        return

    parser = argparse.ArgumentParser(description="Autoexam: automatic questionnaire generation and evaluation.")

    commands = parser.add_subparsers(help="Command option", title="Commands", description="Specific sub-tasks for Autoexam to perform.")

    init_parser = commands.add_parser('init', help='Creates a new Autoexam project.')
    init_parser.add_argument('name', help='Name for the project.')
    init_parser.add_argument('-f', '--folder', help='Override the folder create for the project.')
    init_parser.add_argument('--election', help='Makes the project an election template instead of the standard test template.', action='store_true')
    init_parser.add_argument('--questionnaire', help='Makes the project a questionaire template instead of the standard test template.', action='store_true')
    init_parser.set_defaults(func=init)

    review_parser = commands.add_parser('review', help="Review scanned tests to fix warnings")
    review_parser.add_argument('-v', '--version', help="Specific version to review. If not provided, then the `last` version is reviewed.")
    review_parser.set_defaults(func=review)

    gen_parser = commands.add_parser('gen', help='Generates a new version of the current project.')
    gen_parser.add_argument('-s', '--seed', type=int, default=None, help='A custom seed for the random generator.')
    gen_parser.add_argument('-c', '--tests-count', metavar='N', help="Number of actual tests to generate. If not supplied, only the master file will be generated.", type=int, default=0)
    gen_parser.add_argument('-a', '--answers-per-page', help="Number of answer sections to generate per page. By default is 1. It is up to you to ensure all them fit right in your template.", metavar='N', type=int, default=1)
    gen_parser.add_argument('-t', '--title', help="Title of the test.", default="")
    gen_parser.add_argument('--answer-template', help="Template for the answers sheets.", default="templates/answer_template.tex")
    gen_parser.add_argument('--master-template', help="Template for the master sheet.", default="templates/master_template.tex")
    gen_parser.add_argument('--text-template', help="Template for the text sheets.", default="templates/text_template.tex")
    gen_parser.add_argument('--questions-value', help="Default value for each question.", metavar='N', type=float, default=1.)
    gen_parser.add_argument('--dont-shuffle-tags', help="Disallow shuffling of tags.", action='store_true')
    gen_parser.add_argument('--sort-questions', help="After selecting questions, put them in the same order as in the master.", action='store_true')
    gen_parser.add_argument('--dont-shuffle-options', help="Do not shuffle the options in the questions.", action='store_true')
    gen_parser.add_argument('--dont-generate-text', help="Do not generate text sheets, only answers.", action='store_true')
    gen_parser.add_argument('--election', help="Toggle all options for election mode.", action='store_true')
    gen_parser.add_argument('--questionnaire', help="Toggle all options for questionnaire mode.", action='store_true')
    gen_parser.add_argument('--dont-generate-master', help="Do not generate a master file.", action='store_true')
    gen_parser.set_defaults(func=generate)

    status_parser = commands.add_parser('status', help='Reports various details about the project.')
    status_parser.add_argument('-g', '--generation', help='Add report info about the generation status.', action='store_true')
    status_parser.set_defaults(func=status)

    edit_parser = commands.add_parser('edit', help='Edit the possible source files.')
    edit_parser.add_argument('file', help="The name of the source file to edit.", choices=["master"])
    edit_parser.set_defaults(func=edit)

    stats_parser = commands.add_parser('stats', help='Compiles a series of statistics for the current project.')
    stats_parser.add_argument('-s', '--samples', help='Number of samples to take for simulation-based stats.', default=10000, type=int)
    stats_parser.add_argument('--grades-scale', help='Step of the grading scale to simulate.', default=0.1, type=float)
    stats_parser.set_defaults(func=stats)

    webpoll_parser = commands.add_parser('webpoll', help='Runs the web poll interface.')
    webpoll_parser.add_argument('data', help='The json file to watch.')
    webpoll_parser.add_argument('names', help='The file with all the names.')
    webpoll_parser.add_argument('--extra', help='An extra hand-made list of names and values.')
    webpoll_parser.add_argument('--all', help='Set this to a value to indicate that the given index is equal to vote for everyone.', default=None, type=int)
    webpoll_parser.add_argument('--host', help='The host interface to run in.', default='0.0.0.0')
    webpoll_parser.add_argument('--port', help='The port to run in.', type=int, default=5050)
    webpoll_parser.add_argument('-d', '--debug', help='Run in debug mode.', action='store_true')
    webpoll_parser.set_defaults(func=webpoll)

    simpleui_parser = commands.add_parser('ui', help="Runs the simple web interface.")
    simpleui_parser.add_argument('--host', help='The host interface to run in.', default='0.0.0.0')
    simpleui_parser.add_argument('--port', help='The port to run in.', type=int, default=5000)
    simpleui_parser.add_argument('-d', '--debug', help='Run in debug mode.', action='store_true')
    simpleui_parser.set_defaults(func=simpleui)

    report_parser = commands.add_parser('report', help="Generates several reports for an evaluated test.")
    report_parser.add_argument('data', help='The specific report(s) to generate.', nargs='+', choices=['grades', 'selection', 'partials'])
    report_parser.add_argument('-v', '--version', help='The specific version to report. If not provided then the `last` version is reported.')
    report_parser.add_argument('-f', '--format', help='The format to print results.', choices=['plain', 'simple', 'grid', 'fancy_grid', 'pipe', 'orgtbl', 'rst', 'mediawiki', 'html', 'latex', 'latex_booktabs', 'tsv'])

    report_parser.set_defaults(func=report)

    grade_parser = commands.add_parser('grade', help="Runs the scanned test through the evaluator.")
    grade_parser.add_argument('-v', '--version', help="Specific version to grade. If not provided, then the `last` version is graded.")
    grade_parser.add_argument('-f', '--force', help="Force re-evaluation even if the evaluation already exists. WARNING: This will delete the previous evaluation.", action='store_true')
    grade_parser.set_defaults(func=grade)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
