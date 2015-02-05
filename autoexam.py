#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import sys
import argparse
import shutil


autoexam_source = os.path.dirname(os.path.realpath(__file__))


def src(p):
		return os.path.join(autoexam_source, p)


def is_project_folder():
	try:
		open('.autoexam')
		return True
	except:
		return False


def project_name():
	return open('.autoexam').readline().strip()


def generate(args):
	if not is_project_folder():
		error("You need to be in the root of an Autoexam project folder to do this.")
		return

	name = project_name()

	print("Generating project `{0}`".format(name))


def init(args):
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
	shutil.copytree(src('latex'), dst('templates'))
	shutil.copy(src('example-master.txt'), dst('master.txt'))
	shutil.copy(src('example-config.conf'), dst('config.conf'))
	os.mkdir(dst('generated'))
	open(dst('generated/.gitkeep'), 'w').close()
	open(dst('.gitkeep'), 'w').close()

	f = open(dst('.autoexam'), 'w')
	f.write(args.name)
	f.close()


def error(msg):
	print('')

	for line in msg.split('\n'):
		print("(!) " + line)

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

	args = parser.parse_args()
	args.func(args)


if __name__ == '__main__':
	main()
