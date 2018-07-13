#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Thu 12 Jul 2018 07:23:21 PM CST
# Description:
# TODO: 1. stop的时候应该停止loop的sleep
#       2. stop的时候保证当前已到时刻应该执行的task被执行完毕
#       3. 执行完毕的task要移出outstanding
#########################################################################

import gevent
from datetime import datetime, timedelta
from copy import copy
import logging

def get_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter('[%(asctime)s] %(message)s'))
    sh.setLevel(logging.DEBUG)
    logger.addHandler(sh)
    return logger

logger = get_logger()

class DelayRunner:
    '''run function at a specific point:

    rt: realtime, run it right now
    eoh: run it at end of current hour
    eod: run it at end of current day'''

    def __init__(self):

        self.out_standing_loop_glet = []
        self.out_standing_glet = []
        self.eoh_glet = []
        self.eod_glet = []
        self.is_stop = False

    def __hour_loop(self):
        while True:
            now = datetime.now()
            # TODO: restore after test
            #delta = ((now.replace(microsecond=0, second=0, minute=0) +
            #         timedelta(hours=1))-now).seconds
            delta = ((now.replace(microsecond=0) +
                     timedelta(seconds=1))-now)
            gevent.sleep(delta.total_seconds())
            #logger.debug('start eoh tasks: {}'.format(['{}: {}'.format(g, 'finish' if g.ready() else 'ready') for g in self.eoh_glet]))
            self.__start_glets(self.eoh_glet)

    def __day_loop(self):
        while True:
            now = datetime.now()
            # TODO: restore after test
            #delta = ((now.replace(microsecond=0, second=0, minute=0, hour=0) +
            #         timedelta(days=1))-now).seconds
            delta = ((now.replace(microsecond=0) +
                     timedelta(seconds=2))-now)
            gevent.sleep(delta.total_seconds())
            #logger.debug('start eod tasks: {}'.format(['{}: {}'.format(g, 'finish' if g.ready() else 'ready') for g in self.eod_glet]))
            self.__start_glets(self.eod_glet)

    def __start_glets(self, glet_list):
        for glet in glet_list[:]:
            glet.start()
            glet_list.remove(glet)
            self.out_standing_glet.append(glet)

    def start(self):
        self.is_stop = False
        self.out_standing_loop_glet.extend([
            gevent.spawn(self.__hour_loop),
            gevent.spawn(self.__day_loop)
        ])

    def stop(self):
        self.is_stop = True
        for glet in self.out_standing_loop_glet:
            glet.kill()
        logger.debug('join outstanding glets: {}'.format(['{}: {}'.format(g, 'finish' if g.ready() else 'ready') for g in self.out_standing_glet]))
        gevent.joinall(self.out_standing_glet)

    def safe_clean_run(f):
        def __safe_clea_run(self, func, *args, **kwargs):
            # disallow to run new task after runner is stopped
            if self.is_stop:
                raise RuntimeError('DelayRunner is stopped')
            # remove dead task from outstanding list
            self.out_standing_glet = [glet for glet in self.out_standing_glet if not glet.ready()]
            f(self, func, *args, **kwargs)
        return __safe_clea_run

    @safe_clean_run
    def run_right_now(self, func, *args, **kwargs):
        self.out_standing_glet.append(gevent.spawn(func, *args, **kwargs))

    @safe_clean_run
    def run_at_eoh(self, func, *args, **kwargs):
        self.eoh_glet.append(gevent.Greenlet(func, *args, **kwargs))

    @safe_clean_run
    def run_at_eod(self, func, *args, **kwargs):
        self.eod_glet.append(gevent.Greenlet(func, *args, **kwargs))

if __name__ == '__main__':

    def echo(msg):
        logger.debug(msg)

    delay_runner = DelayRunner()
    delay_runner.start()
    delay_runner.run_right_now(echo, 'rt')
    delay_runner.run_at_eoh(echo, 'eoh1')
    delay_runner.run_at_eod(echo, 'eod1')
    gevent.sleep(1.5)
    delay_runner.run_at_eoh(echo, 'eoh2')
    gevent.sleep(1)
    delay_runner.run_at_eod(echo, 'eod4')
    delay_runner.stop()
