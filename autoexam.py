#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import sys
import argparse
import shutil


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

    name = get_project_option('name')

    print("Generating project `{0}`".format(name))


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
    shutil.copy(src('example-master.txt'), dst('master.txt'))
    shutil.copy(src('example-config.conf'), dst('config.conf'))

    os.mkdir(dst('generated'))
    open(dst('generated/.gitkeep'), 'w').close()

    os.mkdir(dst('.autoexam'))
    os.chdir(folder)

    set_project_option('name', args.name)
    set_project_option('next_version', '1')


def set_project_option(option, value):
    f = open(os.path.join('.autoexam', option), 'w')
    f.write(value)
    f.write('\n')
    f.close()


def get_project_option(option):
    try:
        with open(os.path.join('.autoexam', option), 'r') as fp:
            return fp.readline().strip()
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


def error(msg):
    print('')

    for line in msg.split('\n'):
        print(" (!) ERROR: " + line)

    print('')


def main():
    if 'autoexam.py' in os.listdir('.'):
        error("Please don't run this from inside the Autoexam source folder.\nThis is an evil thing to do that will break the program.")
        return

    parser = argparse.ArgumentParser(description="Autoexam: automatic questionnaire generation and evaluation.")

    commands = parser.add_subparsers(help="Command option", title="Commands", description="Specific sub-tasks for Autoexam to perform.")

    init_parser = commands.add_parser('init', help='Creates a new Autoexam project.')
    init_parser.add_argument('name', help='Name for the project.')
    init_parser.add_argument('-f', '--folder', help='Override the folder create for the project.')
    init_parser.set_defaults(func=init)

    gen_parser = commands.add_parser('gen', help='Generates a new version of the current project.')
    gen_parser.add_argument('-s', '--seed', type=int, help='A custom seed for the random generator.')
    gen_parser.set_defaults(func=generate)

    status_parser = commands.add_parser('status', help='Reports various details about the project.')
    status_parser.add_argument('-g', '--generation', help='Add report info about the generation status.', action='store_true')
    status_parser.set_defaults(func=status)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
