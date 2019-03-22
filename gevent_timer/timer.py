#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Mon 16 Jul 2018 02:20:53 PM CST
# Description:
#########################################################################

import gevent
import gevent.event
import sys

class GTimer:

    # maximum amount of task allowed to be registerd
    __task_limit__ = 128

    class _Task:

        def __init__(self, task_id, interval, is_oneshot, gtimer, func, *args, **kwargs):

            self.id = task_id
            self.interval = interval
            self.is_oneshot = is_oneshot
            self.gtimer = gtimer
            self.func = func
            self.args = args
            self.kwargs = kwargs

            self.stop_evt = gevent.event.Event()
            self.is_start = False

        def _run(self, interval, is_oneshot, func, *args, **kwargs):

            if is_oneshot:
                if isinstance(interval, list):
                    interval = interval[0]
                gevent.sleep(interval)
                func(*args, **kwargs)
                return

            if isinstance(interval, list):
                for _interval in interval:
                    gevent.sleep(_interval)
                    func(*args, **kwargs)
                interval = interval[-1]
            while not self.stop_evt.wait(0):
                gevent.sleep(interval)
                func(*args, **kwargs)

        def start(self):
            if not self.is_start:
                self.stop_evt.clear()
                gr = gevent.Greenlet(self._run, self.interval, self.is_oneshot, self.func, *self.args, **self.kwargs)
                self.gr = gr
                self.gtimer._outstanding_tasks[self.id] = self
                gr.start()
                self.is_start = True

        def stop(self):
            if self.is_start:
                self.stop_evt.set()
                self.is_start = False

        def join(self, timeout):
            if self.gr and self.stop_evt.wait(0):
                self.gtimer._outstanding_tasks.pop(self.id)
                self.gr.join(timeout)
                self.gr.kill()
                self.gr = None

    def __init__(self):

        self._outstanding_tasks = {} # "task_id: _Task" pair
        self._registers = {} # "task_id: _Task" pair

    def register_timer_task(self, interval, is_oneshot, func, *args, **kwargs):
        '''register a new timer task and return task id'''

        def get_smallest_free_task_id(busy_ids, limit):
            if len(busy_ids) >= limit:
                raise RuntimeError('exceeds task amount limit')
            for i in range(0, limit):
                if i not in busy_ids:
                    return i
        task_id = get_smallest_free_task_id(self._registers.keys(), self.__task_limit__)
        task = self._Task(task_id, interval, is_oneshot, self, func, *args, **kwargs)
        self._registers[task_id] = task
        return task_id

    def unregister_timer_task(self, task_id, timeout=1):
        '''unregister specified task_id, stop it beforehead if it has been started'''

        if task_id not in self._registers.keys():
            raise RuntimeError('task id: {} not registerd'.format(task_id))

        # stop the task if it is running
        if task_id in self._outstanding_tasks.keys():
            task = self._outstanding_tasks[task_id]
            task.stop()
            task.join(timeout)
        self._registers.pop(task_id)

    def start(self, task_id = None):
        '''start registered tasks

        if "task_ids" is None, start all registered timer tasks,
        otherwise, only start the specified tasks.'''

        if not task_id:
            for task in self._registers.values():
                task.start()
            return

        if isinstance(task_id, int):
            try:
                self._registers[task_id].start()
                return
            except KeyError as e:
                raise KeyError('task id: {} not registered: {}'.format(task_id, e))
        try:
            for tid in task_id:
                self._registers[tid].start()
        except TypeError as e:
            raise TypeError('task_id must be None, int or iterable: {}'.format(e))

    def stop(self, timeout=1):
        '''stop all registered timer tasks asynchronously'''

        for task in self._registers.values():
            task.stop()
        for task in self._registers.values():
            task.join(timeout)

if __name__ == '__main__':

    def echo(msg):
        print(msg)

    timer = GTimer()
    rick_id = timer.register_timer_task(1, False, echo, 'rick   (1 sec)')
    morty_id = timer.register_timer_task(2, False, echo, 'morty  (2 sec)')
    print('start registered timer tasks...')
    timer.start()

    gevent.sleep(5)
    summer_id = timer.register_timer_task(1, False, echo, 'summer (1 sec)')
    timer.start(summer_id)
    gevent.sleep(5)

    print('stop timer...')
    timer.stop()
    gevent.sleep(3)

    print('start registered timer tasks...')
    timer.start()
    gevent.sleep(5)

    print('unregister rick...')
    timer.unregister_timer_task(rick_id)
    gevent.sleep(5)

    print('unregister morty...')
    timer.unregister_timer_task(morty_id)
    gevent.sleep(5)

    print('stop timer...')
    timer.stop()
    gevent.sleep(5)
