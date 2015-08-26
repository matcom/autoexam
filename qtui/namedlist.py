#! /usr/bin/python
#-*-coding: utf8-*-


def namedlist(class_name, fields):
    class temp(list):
        _indexes = {f:i for (i, f) in enumerate(fields)}
        _fields = fields

        def __init__(self, *values):
            assert len(values) == len(fields)
            super(temp, self).__init__(values)

        def __getattr__(self, name):
            return self[self._indexes[name]]

        def __setattr__(self, name, value):
            self[self._indexes[name]] = value

        def __repr__(self):
            return "%s(%s)" % (class_name, ', '.join('%s=%s'%(f,repr(v)) for f,v in zip(fields, self)))

    temp.__name__ = class_name
    return temp
