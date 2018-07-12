#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Wed 02 May 2018 02:06:57 PM CST
# Description:
#########################################################################

'''Test copy'''

import copy

class Row:
    '''a contained type'''
    def __init__(self, id_, name):
        self.id = id_
        self.name = name
    def __repr__(self):
        return "{}: {}".format(self.id, self.name)

class Table:
    def __init__(self):
        self.rows = {}

    def __add__(self, other):
        out = Table()
        out.rows = copy.deepcopy({**other.rows, **self.rows}) # deepcopy
        return out

    def __sub__(self, other):
        out = Table()
        out.rows = {key: copy.copy(self.rows[key]) for key in set(self.rows.keys()) - set(other.rows.keys())} # shallow copy
        return out

    def __repr__(self):
        out = ''
        for _, row in self.rows.items():
            out += str(row)+'\n'
        return out
