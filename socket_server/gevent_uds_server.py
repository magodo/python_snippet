#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Sun 15 Jul 2018 09:52:49 AM CST
# Description:
#########################################################################

from gevent import monkey; monkey.patch_all()
from gevent.baseserver import BaseServer
import gevent
import abc
import os
import socket

def monkey_patch_gevent_base_server():

    def _extract_family(host):
        if host.startswith('[') and host.endswith(']'):
            host = host[1:-1]
            return socket.AF_INET6, host
        return socket.AF_INET, host

    def _parse_address(address):
        if isinstance(address, tuple):
            if not address[0] or ':' in address[0]:
                return socket.AF_INET6, address
            return socket.AF_INET, address

        if isinstance(address, str):
            if ':' not in address:
                if isinstance(address, int):
                    return socket.AF_INET6, ('', int(address))
                else:
                    return socket.AF_UNIX, address
            else:
                host, port = address.rsplit(':', 1)
                family, host = _extract_family(host)
                if host == '*':
                    host = ''
                return family, (host, int(port))
        raise TypeError('Expected tuple or string, got %s' % type(address))

    from gevent import baseserver
    baseserver._parse_address = _parse_address

monkey_patch_gevent_base_server()

class UDSServer(BaseServer):
    """A UDS server"""

    def __init__(self, *args, **kwargs):
        BaseServer.__init__(self, *args, **kwargs)

    def init_socket(self):
        # in this case, the listender is set beforehead
        if not hasattr(self, 'socket'):
            self.socket = self.get_listener(self.address, family=self.family)
            self.address = self.socket.getsockname()

    @classmethod
    def get_listener(cls, address, family=None):
        return _uds_socket(address, family=family)

    def do_read(self):
        sock = self.socket
        try:
            fd, address = sock._accept()
        except BlockingIOError: # python 2: pylint: disable=undefined-variable
            if not sock.timeout:
                return
            raise
        sock = socket.socket(sock.family, sock.type, sock.proto, fileno=fd)
        return sock, address

    def do_close(self, sock, *args):
        sock.close()

def _uds_socket(address, backlog=50, family=socket.AF_UNIX):
    # backlog argument for compat with tcp_listener
    # pylint:disable=unused-argument

    # we want gevent.socket.socket here
    sock = socket.socket(family=family, type=socket.SOCK_STREAM)
    try:
        sock.bind(address)
    except socket.error as ex:
        strerror = getattr(ex, 'strerror', None)
        if strerror is not None:
            ex.strerror = strerror + ': ' + repr(address)
        raise
    sock.listen(backlog)
    return sock

if __name__ == '__main__':
    def echo(s, address):
        print('new connection: ', address)

    server = UDSServer('/tmp/foo.sock', echo)
    server.serve_forever()
