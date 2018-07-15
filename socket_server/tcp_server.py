#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Tue 10 Jul 2018 09:19:05 PM CST
# Description:
#########################################################################

import socket
import tcp_io
import os
import selectors
import threading
import abc

class Server(abc.ABC):
    def __init__(self, ip, port, uds_entry):
        # init tcp listening socket
        ds = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ds.bind((ip, port))
        ds.listen(5)
        ds.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.data_sock = ds

        # init uds listening socket (for control cmd)
        try:
            os.unlink(uds_entry)
        except OSError:
            if os.path.exists(uds_entry):
                raise
        cs = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        cs.bind(uds_entry)
        cs.listen(1)
        cs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.control_sock = cs
        self.uds_entry = uds_entry

        # multiplexer amongst data and contrl socket
        self.sel = selectors.DefaultSelector()

        # shutdown flag
        self.is_shutdown = False

    def serve(self):
        self.data_sock.setblocking(False)
        self.control_sock.setblocking(False)

        sel = self.sel
        sel.register(self.data_sock, selectors.EVENT_READ, self.__data_accept)
        sel.register(self.control_sock, selectors.EVENT_READ,
                self.__control_accept)

        while not self.is_shutdown:
            events = sel.select(1)
            for key, _ in events:
                callback = key.data
                callback(key.fileobj)

        os.unlink(self.uds_entry)
        self.data_sock.close()
        self.control_sock.close()
        main_th = threading.currentThread()
        for t in threading.enumerate():
            if t == main_th:
                continue
            t.join()

    def stop_serve(self):
        self.is_shutdown = True

    def __data_accept(self, s):
        conn, _ = s.accept()
        conn.setblocking(False)
        t = threading.Thread(target=self.__data_comm, args=(conn, ))
        t.start()

    def __data_comm(self, s):
        reader = tcp_io.Reader(s)
        writer = tcp_io.Writer(s)
        try:
            self.handle_data_comm(reader, writer)
        except RuntimeError as e:
            print(e)
        s.close()

    def __control_accept(self, s):
        conn, _ = s.accept()
        conn.setblocking(False)
        t = threading.Thread(target=self.__control_comm, args=(conn, ))
        t.start()

    def __control_comm(self, s):
        reader = tcp_io.Reader(s)
        writer = tcp_io.Writer(s)
        try:
            self.handle_control_comm(reader, writer)
        except RuntimeError as e:
            print(e)
        s.close()

    @abc.abstractmethod
    def handle_data_comm(self, reader, writer):
        pass

    @abc.abstractmethod
    def handle_control_comm(self, reader, writer):
        pass

if __name__ == '__main__':

    class StoppableEchoServer(Server):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def handle_data_comm(self, r, w):
            print("data comm: ENTER")
            msg = r.read_packet()
            w.write_packet(msg)
            print("data comm: LEAVE")

        def handle_control_comm(self, r, w):
            print("control comm: ENTER")
            msg = r.read_packet()
            if msg.decode('ascii') == 'stop':
                self.stop_serve()
            print("control comm: LEAVE")

    s = StoppableEchoServer(socket.gethostname(), 30086, 'foobar.sock')
    s.serve()
