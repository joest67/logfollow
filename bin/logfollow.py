"""Collect log from pushers with using TCP connection or ZMQ sockets."""

import socket
import logging
import os.path

from tornado import stack_context, ioloop
from tornado.netutil import TCPServer
from tornado.options import define, options, parse_command_line
from tornado.httpserver import HTTPServer
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.util import b, bytes_type
from tornado.escape import json_encode

from tornadio import server, get_router, SocketConnection

class LogServer(TCPServer):
    """Handle incoming TCP connections from log pusher clients"""

    def handle_stream(self, stream, address):
        """Called when new IOStream object is ready for usage"""
        logging.debug('Incoming connection from %r', address)
        LogConnection(stream, address, server=self)

class LogConnection(object):
    """Handle each IOStream for incoming log pusher connections"""

    logs = set()

    def __init__(self, stream, address, server):
        """Initialize base params and call stream reader for next line"""
        self.stream = stream
        if self.stream.socket.family not in (socket.AF_INET, socket.AF_INET6):
            # Unix (or other) socket; fake the remote address
            address = ('0.0.0.0', 0)
        self.address = address
        self.server = server

        self._disconnect_callback = stack_context.wrap(self._on_disconnect)
        self.stream.set_close_callback(self._disconnect_callback)

        self._read_callback = stack_context.wrap(self._on_read)
        self._head_callback = stack_context.wrap(self._on_head)
        self.stream.read_until(b("\n"), self._head_callback)


    def _on_head(self, line):
        """Extract information about log file path.

        To use this, you should call tail util with -v param.
        If you use ZMQ sockets, you can push file name with
        socket identity signiture.
        """
        line = line.strip()
        logging.info(line)
        self.filepath = line.split()[1]
        self.__class__.logs.add(self.filepath)
        self.wait()

    def _on_read(self, line):
        """Called when new line received from connection"""
        message = line.strip()
        logging.info(message)
        formatted = dict(message = 'log', content = message,
                         identity = [self.filepath, self.address[0]])
        ClientConnection.broadcast(formatted)
        self.wait()

    def wait(self):
        self.stream.read_until(b("\n"), self._read_callback)

    def _on_disconnect(self, *args, **kwargs):
        self.__class__.logs.remove(self.filepath)
        logging.debug('Client disconnected %r', self.address)

class BroadcastHandler(RequestHandler):
    def get(self):
        self.render(os.path.join(options.templates, 'console.html'))

    def post(self):
        message = self.get_argument('message')
        key = self.get_argument('id', None)
        for client in ClientConnection.clients:
            if key and not key == client.id:
                continue
            client.send(message)
        self.write('message send.')


class ClientConnection(SocketConnection):
    clients = set()

    def __init__(self, *args, **kwargs):
        self.id = None
        super(ClientConnection, self).__init__(*args, **kwargs)

    @classmethod
    def broadcast(cls, message):
        """Send JSON encoded message to all connected clients"""
        json = json_encode(message)
        for client in cls.clients:
            client.send(json)

    def on_open(self, *args, **kwargs):
        """Called when new connection from client created"""
        logging.debug('client connected')
        self.clients.add(self)
        self.send(json_encode(dict(message = 'connection',
                                   logs = list(LogConnection.logs))))

    def on_message(self, message):
        logging.info(message)
        if not self.id:
            self.id = message.get('id', None)
        self.send(json_encode(dict(message = 'sign', sign = self.id)))

    def on_close(self):
        """Called when connection is closed"""
        logging.debug('client disconnected')
        self.clients.remove(self)

class LogTracer(Application):
    """Application object. Provide routing configuration."""

    def __init__(self):
        super(LogTracer, self).__init__([
            (r"/static/(.*)", StaticFileHandler, dict(path='/etc/logfollow/')),
            (r"/", BroadcastHandler),
            get_router(ClientConnection).route()
        ], debug=options.debug)


def start():
    io_loop = ioloop.IOLoop.instance()

    tcp_server = LogServer(io_loop=io_loop)
    tcp_server.listen(options.gateway)
    logging.debug('Start TCP server on %r port', options.gateway)

    server.SocketServer(LogTracer(), io_loop=io_loop)
    logging.debug('Start HTTP server on %r port', options.port)

    io_loop.start()

define('debug', default=True, type=bool)
define('port', default=6767, type=int)
define('gateway', default=6777, type=int)
define('templates', default='/etc/logfollow', type=str)

if __name__ == '__main__':
    parse_command_line()
    start()

