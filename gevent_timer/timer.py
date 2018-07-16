#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Mon 16 Jul 2018 02:20:53 PM CST
# Description:
#########################################################################

import gevent


class GTimer:

    class _Task:

        def __init__(self, task_id, interval, is_oneshot, gtimer, func, *args, **kwargs):

            self.id = task_id
            self.interval = interval
            self.is_oneshot = is_oneshot
            self.gtimer = gtimer
            self.func = func
            self.args = args
            self.kwargs = kwargs

            self.is_start = False

        def _run(self, interval, is_oneshot, func, *args, **kwargs):

            if is_oneshot:
                gevent.sleep(interval)
                func(*args, **kwargs)
                return
            while True:
                gevent.sleep(interval)
                func(*args, **kwargs)

        def start(self):

            if not self.is_start:
                self.is_start = True
                gr = gevent.spawn(self._run, self.interval, self.is_oneshot, self.func, *self.args, **self.kwargs)
                self.gr = gr
                self.gtimer._outstanding_tasks[self.id] = self

        def stop(self):

            if self.is_start:
                self.is_start = False
                self.gtimer._outstanding_tasks.pop(self.id)
                self.gr.kill()
                self.gr = None

    def __init__(self):

        self._outstanding_tasks = {} # "task_id: _Task" pair
        self._registers = {} # "task_id: _Task" pair

    def register_timer_task(self, task_id, interval, is_oneshot, func, *args, **kwargs):
        '''register a new timer task and return it for later usage(e.g. start)'''

        if task_id not in self._registers.keys():
            task = self._Task(task_id, interval, is_oneshot, self, func, *args, **kwargs)
            self._registers[task_id] = task
            return task

    def unregister_timer_task(self, task_id):
        '''unregister specified task_id, stop it beforehead if it has been started'''

        if task_id in self._registers.keys():
            if task_id in self._outstanding_tasks.keys():
                task = self._outstanding_tasks[task_id]
                task.stop()
            self._registers.pop(task_id)

    def start(self):
        '''start all registered timer tasks'''

        for task in self._registers.values():
            task.start()

    def stop(self):
        '''stop all registered timer tasks asynchronously'''

        for task in self._registers.values():
            task.stop()

if __name__ == '__main__':

    def echo(msg):
        print(msg)

    timer = GTimer()
    timer.register_timer_task(1, 1, False, echo, '1-1sec')
    timer.register_timer_task(2, 2, False, echo, '2-2sec')
    print('start registered timer tasks...')
    timer.start()

    gevent.sleep(5)
    t = timer.register_timer_task(3, 1, False, echo, '3-1sec')
    print('start another timer task...')
    t.start()
    gevent.sleep(5)

    print('stop all timer task...')
    timer.stop()
    gevent.sleep(3)

    print('start registered timer tasks...')
    timer.start()
    gevent.sleep(5)

    print('unregister one timer task...')
    timer.unregister_timer_task(1)
    gevent.sleep(5)


    print('unregister remaining timer tasks...')
    timer.unregister_timer_task(2)
    timer.unregister_timer_task(3)
    gevent.sleep(5)
