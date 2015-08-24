#! /usr/bin/python
#-*-coding: utf8-*-

"""
Project:
- name
- total_questions
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


Project = namedlist('Project', ['name', 'total_questions', 'total_exams', 'tags', 'questions'])
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
    t1 = Tag('t1', 3)
    a1 = Answer(True, False, 'anstxt')
    q1 = Question('a', ['t1'], 'qtxt', [a1, a1])
    p1 = Project('p1', 2, 2, [t1], [q1, q1])
    s = json.dumps(p1)
    print("hello", s)
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
