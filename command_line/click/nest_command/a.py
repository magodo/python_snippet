#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Wed 25 Apr 2018 06:21:02 PM CST
# Description: Nest group in group.
#########################################################################

import click
from b.b import cli as b_cli
from c.c import cli as c_cli

@click.group()
def cli():
    pass

cli.add_command(b_cli, name='b')
cli.add_command(c_cli, name='c')

if __name__ == '__main__':
    cli()
