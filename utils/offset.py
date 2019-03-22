#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Thu 27 Sep 2018 04:59:13 PM CST
# Description:
#########################################################################

##
# 0: filename
# 1: line
# 2: col

import sys

def offset(filename, line, column):
    with open(filename, 'r') as f:
        content = f.read()
    content = bytes(content, encoding = 'utf8')
    print(content)

    current_line = 1
    current_column = 1
    newline = bytes( b'\n' )[ 0 ]
    for i, byte in enumerate( content ):
        if current_line == line and current_column == column:
            return i
        current_column += 1
        if byte == newline:
            current_line += 1
            current_column = 1
    raise RuntimeError("")

if __name__ == '__main__':
    print(offset(sys.argv[1], int(sys.argv[2]), int(sys.argv[3])))
