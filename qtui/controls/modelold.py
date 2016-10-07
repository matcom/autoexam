#! /usr/bin/python
#-*-coding: utf8-*-

"""
this is is a mirror for ../../model.py
"""

import imputil

imputil.imp.load_source('namedlist', 'namedlist.py')

source = imputil.imp.load_source('model', 'model.py')

Project = source.Project
Tag = source.Tag
Question = source.Question
Answer = source.Answer
