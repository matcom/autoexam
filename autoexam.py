#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import argparse


def generate(args):
	pass


def init(args):
	print(args.name)


def main():
	parser = argparse.ArgumentParser(description="Autoexam: automatic questionnaire generation and evaluation.")

	commands = parser.add_subparsers(help="Command option", title="Commands", description="Specific sub-tasks for Autoexam to perform.")

	init_parser = commands.add_parser('init', help='Creates a new Autoexam project.')
	init_parser.add_argument('name', help='Name for the project.')
	init_parser.set_defaults(func=init)

	gen_parser = commands.add_parser('generate', help='Generates a new version of the current project.')
	gen_parser.add_argument('-s', '--seed', type=int, help='A custom seed for the random generator.')
	gen_parser.set_defaults(func=generate)

	args = parser.parse_args()


if __name__ == '__main__':
	main()
