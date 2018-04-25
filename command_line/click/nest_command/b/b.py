#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Wed 25 Apr 2018 07:51:15 PM CST
# Description:
#########################################################################

import click

@click.group()
def cli():
    pass

@cli.command()
def foo():
    pass

@cli.command()
def bar():
    pass
