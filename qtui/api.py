#! /usr/bin/python
#-*-coding: utf8-*-

"""
autoexam api
"""

import os, subprocess, random, jinja2
import sys
import autoexam

master = 'master.txt'
# project_path = None


# region Helpers

def get_flag(kwargs, flag):
    if kwargs.get(flag) == True:
        return '--' + flag.replace('_', '-')
    return ''


def get_value(kwargs, field, default=None):
    value = kwargs.get(field, default)
    if value != None:
        return '--' + field.replace('_', '-') + ' ' + str(value)
    return ''


def run(command):
    # current_path = os.getcwd()
    # os.chdir(project_path)
    value = os.system(command)
    # os.chdir(current_path)
    return value


# def set_project_path(path):
#     global project_path
#     project_path = path


def save_master(master_text):
    with open(master, 'w') as fp:
        fp.write(master_text)
# endregion Helpers

# region Autoexam Methods

def init(name, folder='.', template='', **kwargs):
    """
    kwargs:
    =======
    @folder: project folder
    @election: (...)
    @questionnaire: (...)
    """

    folder = '-f "%s"'%folder
    # folder = get_value(kwargs, 'folder', '.')

    election = get_flag(kwargs, 'election')
    questionnaire = get_flag(kwargs, 'questionnaire')

    # params = [autoexam, 'init', folder, election, questionnaire, '"%s"'%name]
    params = ['autoexam', 'init', folder, '"%s"'%name]

    cmd = ' '.join(params)
    return os.system(cmd)


def gen(**kwargs):
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

    seed = get_value(kwargs, 'seed', random.randint(0, 2**64 - 1))
    tests_count = get_value(kwargs, 'tests_count', 1)
    answers_per_page = get_value(kwargs, 'answers_per_page', 1)
    title = get_value(kwargs, 'title')
    answer_template = get_value(kwargs, 'answer_template')
    master_template = get_value(kwargs, 'master_template')
    text_template = get_value(kwargs, 'text_template')
    questions_value = get_value(kwargs, 'questions_value')

    dont_shuffle_tags = get_flag(kwargs, 'dont_shuffle_tags')
    sort_questions = get_flag(kwargs, 'sort_questions')
    dont_shuffle_options = get_flag(kwargs, 'dont_shuffle_options')
    dont_generate_text = get_flag(kwargs, 'dont_generate_text')
    election = get_flag(kwargs, 'election')
    questionnaire = get_flag(kwargs, 'questionnaire')
    dont_generate_master = get_flag(kwargs, 'dont_generate_master')

    params = ['autoexam', 'gen', seed, tests_count, answers_per_page,
    title, answer_template, master_template, text_template,
    questions_value, dont_shuffle_tags, sort_questions, dont_shuffle_options,
    dont_generate_text, election, questionnaire, dont_generate_master]

    cmd = ' '.join(params)
    return run(cmd)

# endregion Autoexam methods


def validate_project(project):
    for question in project.questions:
        if not question.tag_names:
            # TODO: Tr (translator)
            raise Exception("Debe haber al menos una etiqueta por pregunta")


def render_master(project, template_path):
    return jinja2.Template(open(template_path).read().decode('utf-8')).render(project=project)


def add_scan_event_subscriber(obj):
    autoexam.add_scan_subscriber(obj)


def remove_scan_event_subscriber(obj):
    autoexam.remove_scan_subscriber(obj)


def scan(_args):
    autoexam.scan(_args)
