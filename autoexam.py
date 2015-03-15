#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import sys
import argparse
import shutil

import gen

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


def stats(args):
    if not check_project_folder():
        return

    build_stats(args)


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

    gen_parser = commands.add_parser('gen', help='Generates a new version of the current project.')
    gen_parser.add_argument('-s', '--seed', type=int, help='A custom seed for the random generator.')

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

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
