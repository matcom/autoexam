#! /usr/bin/python
#-*-coding: utf8-*-

"""
Project:
- name
- total_questions_per_exam
- tags
- questions

Tag:
- name
- min_questions

Question:
- id
- tag_names
- text
- answers

Answer:
- valid
- fixed_position
- text
"""

import json
from namedlist import namedlist

data = {}

Project = namedlist('Project', ['name', 'total_questions_per_exam', 'total_exams_to_generate', 'tags', 'questions'])
Tag = namedlist('Tag', ['name', 'min_questions'])
Question = namedlist('Question', ['id', 'tag_names', 'text', 'answers'])
Answer = namedlist('Answer', ['valid', 'fixed_position', 'text'])


def dump_project(proj, path):
    with open(path, 'w') as fp:
        json.dump(proj, fp)


def load_project(path):
    with open(path, 'r') as fp:
        proj = json.load(fp)
        # loading project
        proj = Project(*proj)

        # loading tags
        for i,t in enumerate(proj.tags):
            proj.tags[i] = Tag(*t)
        # loading questions
        for i,q in enumerate(proj.questions):
            question = Question(*q)
            proj.questions[i] = question
            # loading answers
            for j,a in enumerate(question.answers):
                question.answers[j] = Answer(*a)
        return proj


def test():
    t1 = Tag('tag', 3)
    a1 = Answer(True, False, 'This is an answer')
    a2 = Answer(True, False, 'This is another answer')
    q1 = Question('a', ['t1'], 'This is a question', [a1, a2])
    q2 = Question('a', ['t1'], 'This is another question', [a1, a2])
    p1 = Project('Project 1', 2, 2, [t1], [q1, q2])

    s = json.dumps(p1)
    print(s)
    proj = json.loads(s)
    proj = Project(*proj)
    # loading tags
    for i,t in enumerate(proj.tags):
        print("tag:", t)
        proj.tags[i] = Tag(*t)
    # loading questions
    for i,q in enumerate(proj.questions):
        question = Question(*q)
        proj.questions[i] = question
        # loading answers
        for j,a in enumerate(question.answers):
            question.answers[j] = Answer(*a)
            print("answer:", question.answers[j])


if __name__ == '__main__':
    test()
