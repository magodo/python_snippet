#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Sun 15 Jul 2018 12:41:14 PM CST
# Description:
#########################################################################

from gevent_uds_server import UDSServer
from tcp_io import Reader
from gevent.server import StreamServer
import gevent
import os
import abc

class Server(abc.ABC):

    def __init__(self, ip, port, uds_entry):
        # Cache the tcp server init info and delay creating it until starting,
        # this is because of the implementation of StreamServer that when it is
        # stopped, it will uninitialize everything, hence another start will
        # need to create a new instance of it.
        self.ip = ip
        self.port = port
        self.data_server = None
        self.gr_data_server = None

        try:
            os.unlink(uds_entry)
        except OSError:
            if os.path.exists(uds_entry):
                raise
        self.control_server = UDSServer(uds_entry, self.handle_control)

        self.is_start = False

    def serve_forever(self):
        self._start_data_server()
        self.control_server.serve_forever()

    def _start_data_server(self):
        if not self.is_start:
            self.is_start = True
            print('data server starting...')
            # spawn set capacity of pool so that on stop, any outstanding connection will be terminated
            self.data_server = StreamServer((self.ip, self.port), self.handle_data, spawn=20)
            self.gr_data_server = gevent.spawn(self.data_server.serve_forever)
            print('data server started')

    def _stop_data_server(self):
        if self.is_start:
            self.is_start = False
            print('data server stopping')
            self.data_server.stop()
            print('data server waiting for outstanding task...')
            self.gr_data_server.join()
            print('data server stopped')

    @abc.abstractmethod
    def handle_data(self, sock, address):
        pass

    def handle_control(self, sock, address):
        r = Reader(sock)
        msg = r.read_packet()
        print('get control msg: ', msg)
        if msg == b'stop':
            self._stop_data_server()
        elif msg == b'start':
            self._start_data_server()

if __name__ == '__main__':

    from tcp_io import Writer
    import socket

    class StoppableEchoServer(Server):

        def __init__(self, ip, port, uds_entry):
            super().__init__(ip, port, uds_entry)

        def handle_data(self, s, addr):
            r = Reader(s)
            w = Writer(s)
            msg = r.read_packet()
            w.write_packet(msg)

    s = StoppableEchoServer(socket.gethostname(), 10086, '/tmp/foo.sock')
    s.serve_forever()
