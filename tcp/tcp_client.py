#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Wed 11 Jul 2018 01:23:34 PM CST
# Description:
#########################################################################

import socket
import tcp_io
import abc

class Client(abc.ABC):

    def __init__(self, ip, port, uds_entry):
        self.ip = ip
        self.port = port
        self.uds_entry = uds_entry

        # init tcp listening socket
        ds = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_sock = ds

        # init uds listening socket (for control cmd)
        cs = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.control_sock = cs

    def data_comm(self):
        self.data_sock.connect((self.ip, self.port))
        reader = tcp_io.Reader(self.data_sock)
        writer = tcp_io.Writer(self.data_sock)
        self.handle_data_comm(reader, writer)

    def control_comm(self):
        self.control_sock.connect(self.uds_entry)
        reader = tcp_io.Reader(self.control_sock)
        writer = tcp_io.Writer(self.control_sock)
        self.handle_control_comm(reader, writer)

    @abc.abstractmethod
    def handle_data_comm(self, r, w):
        pass

    @abc.abstractmethod
    def handle_control_comm(self, r, w):
        pass

if __name__ == '__main__':

    class MyClient(Client):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def handle_data_comm(self, r, w):
            w.write_packet('hello world'.encode('ascii'))
            msg = r.read_packet()
            print(msg.decode('ascii'))

        def handle_control_comm(self, r, w):
            w.write_packet('stop'.encode('ascii'))

    client = MyClient(socket.gethostname(), 30086, 'foobar.sock')
    client.data_comm()
    client.control_comm()
