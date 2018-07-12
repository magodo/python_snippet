#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Wed 25 Apr 2018 07:51:15 PM CST
# Description:
#########################################################################

import click

@click.group('run', help='run')
@click.argument('a', nargs=1)
def cli(a):
    pass

@cli.command('foo', help='foo')
def foo():
    pass

@cli.command('bar', help='bar')
def bar():
    pass

if __name__ == '__main__':
    cli()
