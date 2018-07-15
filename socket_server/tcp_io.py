#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Tue 10 Jul 2018 05:04:50 PM CST
# Description:
#########################################################################

import struct

class Reader:
    '''Read full packet whose first 4 bytes indicate length of following message(in BE order).'''

    def __init__(self, sock):
        self.sock = sock

    def read_packet(self):
        '''read a complete message from socket'''
        length = self.__read_head_len()
        return self.__read_full(length)

    def __read_head_len(self):
        '''read length of message header.'''
        length = self.__read_full(4)
        return struct.unpack('>I', length)[0]

    def __read_full(self, msg_len):
        recv_bytes = b""
        nrecv = 0
        while nrecv < msg_len:
            data = self.sock.recv(msg_len-nrecv)
            if data == b'':
                raise RuntimeError("socket connection broken")
            nrecv += len(data)
            recv_bytes += data
        return recv_bytes

class Writer:
    '''Write full packet, prepending first 4 bytes indicate length of following message(in BE order).'''

    def __init__(self, sock):
        self.sock = sock

    def write_packet(self, bin_msg):
        '''write a complete message to socket'''
        header = struct.pack('>I', len(bin_msg))
        bin_msg = header + bin_msg
        msg_len = len(bin_msg)
        totalsent = 0
        while totalsent < msg_len:
            sent = self.sock.send(bin_msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent += sent
