#! /usr/bin/env python2.5
# -*- coding: utf-8 -*-
# vim: set expandtab :


from __future__ import with_statement

import SocketServer
import sys


__author__ = 'Alexandru Moșoi <brtzsnr@gmail.com>'


class UDPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        sys.stdout.write(self.request[0])
        sys.stdout.flush()


if __name__ == '__main__':
    if len(sys.argv) == 1 or len(sys.argv) > 4:
        print >>sys.stderr, 'Simple UDP listener. Dumps datagrams to stdout. Usage:'
        print >>sys.stderr, '\t%s [host] port - listens on host:port (host defaults to localhost).' % sys.argv[0]
        sys.exit()

    port = None
    host = None
    outp = None

    if len(sys.argv) == 2:  # port
        host, port = 'localhost', int(sys.argv[1])
    elif len(sys.argv) == 3:  # host port
        host, port = sys.argv[1:]

    SocketServer.UDPServer((host, port), UDPHandler).serve_forever()
