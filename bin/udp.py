#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""A UDP listener.

This module is intended to be a simple replacement for netcat

"""

import SocketServer
import sys


class UDPHandler(SocketServer.BaseRequestHandler):
    """A simple UDP handler which dumps datagrams to stdout"""
    def handle(self):
        """Dumps datagrams to stdout"""
        sys.stdout.write(self.request[0])
        sys.stdout.flush()


def main():
    """Starts the UDP server"""
    if not 2 <= len(sys.argv) <= 3:
        print >> sys.stderr, 'A simple UDP listener which dumps',
        print >> sys.stderr, 'datagrams to stdout. Usage:'
        print >> sys.stderr, '\t%s [host] port - listens' % sys.argv[0],
        print >> sys.stderr, 'on host:port (host defaults to localhost).'
        exit()

    port = None
    host = None

    if len(sys.argv) == 2:  # port
        host, port = 'localhost', int(sys.argv[1])
    elif len(sys.argv) == 3:  # host port
        host, port = sys.argv[1:]

    SocketServer.UDPServer((host, port), UDPHandler).serve_forever()


if __name__ == '__main__':
    main()
