#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Wed 25 Apr 2018 03:29:55 PM CST
# Description:
#########################################################################

import click
from foo import foo

@click.group()
def cli():
    pass

@click.command()
@click.argument('word')
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name',
              help='The person to greet.')
def hello(word, count, name):
    for x in range(count):
        click.echo('Hello {}, {}!'.format(name, word))

if __name__ == '__main__':

    cli.add_command(hello)
    cli.add_command(foo)
    cli()

