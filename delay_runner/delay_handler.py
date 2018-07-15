#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Thu 12 Jul 2018 07:23:21 PM CST
# Description: 在特定事件批量执行一次(即只有一个gr)
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

class DelayHandler:
    '''run function at a specific point:

    rt: realtime, run it right now
    eoh: run it at end of current hour
    eod: run it at end of current day'''

    def __init__(self, batch_handle_func):

        self.batch_handle_func = batch_handle_func
        self.out_standing_loop_glet = []
        self.out_standing_glet = []
        self.eoh_objs = []
        self.eod_objs = []
        self.is_stop = False

    def __hour_loop(self):
        while True:
            now = datetime.now()
            delta = ((now.replace(microsecond=0, second=0, minute=0) +
                     timedelta(hours=1))-now).total_seconds()
            #delta = ((now.replace(microsecond=0) +
            #         timedelta(seconds=1))-now).total_seconds()
            gevent.sleep(delta)
            #logger.debug('start eoh tasks: {}'.format(['{}: {}'.format(g, 'finish' if g.ready() else 'ready') for g in self.eoh_glet]))
            self.__start_handler(self.eoh_objs)

    def __day_loop(self):
        while True:
            now = datetime.now()
            delta = ((now.replace(microsecond=0, second=0, minute=0, hour=0) +
                     timedelta(days=1))-now).total_seconds()
            #delta = ((now.replace(microsecond=0) +
            #         timedelta(seconds=2))-now).total_seconds()
            gevent.sleep(delta)
            #logger.debug('start eod tasks: {}'.format(['{}: {}'.format(g, 'finish' if g.ready() else 'ready') for g in self.eod_glet]))
            self.__start_handler(self.eod_objs)

    def __start_handler(self, obj_list):
        if obj_list:
            glet = gevent.spawn(self.batch_handle_func, obj_list[:])
            self.out_standing_glet.append(glet)
            obj_list.clear()

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
        #logger.debug('join outstanding glets: {}'.format(['{}: {}'.format(g, 'finish' if g.ready() else 'ready') for g in self.out_standing_glet]))
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
    def handle_now(self, obj):
        self.out_standing_glet.append(gevent.spawn(self.batch_handle_func, [obj]))

    @safe_clean_run
    def handle_at_eoh(self, obj):
        self.eoh_objs.append(obj)

    @safe_clean_run
    def handle_at_eod(self, obj):
        self.eod_objs.append(obj)

if __name__ == '__main__':

    def echo(msg_list):
        logger.debug(" ".join(msg_list))

    h = DelayHandler(echo)
    h.start()
    h.handle_now('rt')
    h.handle_at_eoh('eoh1')
    h.handle_at_eoh('eoh2')
    h.handle_at_eod('eod1')
    h.handle_at_eod('eod2')
    gevent.sleep(1.5)
    h.handle_at_eoh('eoh3')
    h.handle_at_eoh('eoh4')
    gevent.sleep(1)
    h.handle_at_eod('eod3')
    h.stop()
