#! /usr/bin/python
#-*-coding: utf8-*-

"""
autoexam api
"""

import os, subprocess, random

autoexam = 'python autoexam.py'


def get_flag(kwargs, flag):
    if kwargs.get(flag) == True:
        return '--' + flag.replace('_', '-')
    return ''


def get_value(kwargs, field, default=None):
    value = kwargs.get(field, default)
    if value != None:
        return '--' + flag.replace('_', '-') + ' ' + str(value)
    return ''


def init(self, name, folder='.', template='', **kwargs):
    """
    kwargs:
    =======
    @folder: project folder
    @election: (...)
    @questionnaire: (...)
    """

    folder = get_value(kwargs, 'folder', '.')

    election = s(kwargs, 'election')
    questionnaire = get_flag(kwargs, 'questionnaire')

    if not os.path.isdir(folder):
        raise AttributeError('"%s" is not a directory')

    params = [autoexam, 'init', folder, election, questionnaire, name]

    cmd = ' '.join(params)
    return subprocess.wait(cmd)


def gen(self, **kwargs):
    """
    kwargs:
    =======
    @seed: (...)
    @tests_count: (...)
    @answers_per_page: (...)
    @title: (...)
    @answer_template: (...)
    @master_template: (...)
    @text_template: (...)
    @questions_value: (...)
    @dont_shuffle_tags: (...)
    @sort_questions: (...)
    @dont_shuffle_options: (...)
    @dont_generate_text: (...)
    @election: (...)
    @questionnaire: (...)
    @dont_generate_master: (...)
    """

    seed = get_value(kwargs, 'seed', random.random())
    tests_count = get_value(kwargs, 'tests_count', 1)
    answers_per_page = get_value(kwargs, 'answers_per_page', 1)
    title = get_value(kwargs, 'title')
    answer_template = get_value(kwargs, 'answer_template')
    master_template = get_value(kwargs, 'master_template')
    text_template = get_value(kwargs, 'text_template')
    questions_value = get_value(kwargs, 'questions_value')

    dont_shuffle_tags = get_flag(kwargs, dont_shuffle_tags)
    sort_questions = get_flag(kwargs, sort_questions)
    dont_shuffle_options = get_flag(kwargs, dont_shuffle_options)
    dont_generate_text = get_flag(kwargs, dont_generate_text)
    election = get_flag(kwargs, election)
    questionnaire = get_flag(kwargs, questionnaire)
    dont_generate_master = get_flag(kwargs, dont_generate_master)

    params = [autoexam, 'gen', seed, tests_count, answers_per_page,
    title, answer_template, master_template, text_template,
    questions_value, dont_shuffle_tags, sort_questions, dont_shuffle_options,
    dont_generate_text, election, questionnaire, dont_generate_master]

    cmd = ' '.join(params)
    return subprocess.wait(cmd)
