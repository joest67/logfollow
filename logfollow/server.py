"""Application handlers and servers"""

import os
import os.path
import socket
import logging

from tornado import stack_context, ioloop
from tornado.netutil import TCPServer
from tornado.httpserver import HTTPServer
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.escape import json_encode, json_decode
from tornado.util import b, bytes_type

from tornadio import server, get_router, SocketConnection
from logfollow import ui
from logfollow.protocol import Message

class LogStreamer(object):
    """Call subprocessed for streaming logs"""

    streams = dict()

    @classmethod
    def follow(cls, path, follower):
        """Add additional follower to tail or start streamer if path is new"""
    
        if path in cls.streams:
            cls.streams[path]['followers'].add(follower)
        else:
            try:
                # Check file's validity to work with
                with open(path):
                    cls.streams[path] = dict(pid=cls._run(path), restart=0,
                                             followers=set([follower]))
            except (IOError, OSError), e:
                # Send error notification to user
                follower.send(str(Message.FollowError(path, e)))
                return False

        # Send notification to user 
        follower.send(str(Message.FollowOk(path)))
        return True

    @classmethod
    def _run(cls, path):
        """Save subprocess PID in order to check periodicaly"""
        return os.spawnl(os.P_NOWAIT, cls._command(path))

    @classmethod
    def unfollow(cls, path, follower):
        """Remove client from list of followers"""
        try:
            cls.streams[path]['followers'].remove(follower)
        except (KeyError, TypeError):
            pass

    @classmethod
    def check(cls):
        """Check PID for each streamer subprocess"""
        for path, stream in cls.streams:
            if not os.path.exists('/proc/%d' % stream['pid']):
                # Process stopped
                # TODO: Send notification to each user
                cls.restart(path)

    @classmethod
    def restart(cls, path):
        """Restart streaming process for given path"""
        if path in cls.streams and not cls.streams[path].get('is_restarting', False):
            # Timeout will be changed from 1 to 32 seconds
            deadline = time.time() + 2 ** min(cls.streams[path].get('restart', 0), 5)

            cls.streams[path]['is_restarting'] = True
            cls.streams[path]['restart'] += 1

            logging.warning('Restart streamer for %s in %d sec', path, deadline)

            ioloop.IOLoop.instance().add_timeout(deadline, 
                partial(cls._restart_timeout, path=path))

    @classmethod
    def _restart_timeout(cls, path):
        """Do restart after timeout"""
        # TODO: Catch errors 
        cls.streams[path]['pid'] = cls._run(path)
        cls.streams[path]['is_restarting'] = False 

    @staticmethod
    def _command(path):
        """Generate command for log stream run"""
        return 'tail -f -v %s | nc 127.0.0.1 %d' % (path, options.gateway)

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
        self.__class__.logs.add(str(self))
        self.wait()

    def _on_read(self, line):
        """Called when new line received from connection"""
        protocol = dict(type = 'entry', entries = [line.strip()],
                        log = str(self), time=time.time())
        ClientConnection.broadcast(protocol)
        self.wait()

    def wait(self):
        self.stream.read_until(b("\n"), self._read_callback)

    def _on_disconnect(self, *args, **kwargs):
        self.__class__.logs.remove(str(self))
        logging.debug('Client disconnected %r', self.address)

    def __str__(self):
        """Build string representation, will be used for working with
        server identity (not only file path) in future"""
        return self.filepath

class DashboardHandler(RequestHandler):
    """Render HTML page with user's dashboard"""

    def get(self):
        self.render(os.path.join(self.application.options.templates, 'console.html'))
        
class ClientConnection(SocketConnection):
    clients = set()

    def __init__(self, *args, **kwargs):
        self.follow = set()
        super(ClientConnection, self).__init__(*args, **kwargs)

    @classmethod
    def broadcast(cls, message):
        """Send JSON encoded message to all connected clients"""
        logging.info('Broadcasting: %s', message)
        for client in cls.clients:
            if message['log'] in client.follow:
                client.send(message)

    def on_open(self, request, *args, **kwargs):
        """Called when new connection from client created"""
        logging.debug('Client connected: %s', self)
        self.open_request = request
        self.clients.add(self)

    def on_message(self, message):
        """Called when protocol package received from client"""
        logging.info('Received from client: %s', message)
        self._command(message)

    def on_close(self):
        """Called when connection is closed"""
        logging.debug('Client disconnected: %s', self)
        self.clients.remove(self)

    def _command(self, protocol):
        if protocol['command'] == 'follow':
            self.follow = self.follow.union(set(protocol['logs']))
            for log in protocol['logs']:
                LogStreamer.follow(log, self)
        elif protocol['command'] == 'unfollow':
            self.follow -= set(protocol['logs'])
            for log in protocol['logs']:
                LogStreamer.unfollow(log, self)
        else:
            response = dict(type='status',
                            status='ERROR',
                            description='Undefined command')
            self.send(response)

class LogTracer(Application):
    """Application object. Provide routing configuration."""

    def __init__(self, options):
        self.options = options
        settings = dict(debug=options.debug, 
                        socket_io_port=options.port, 
                        ui_modules=ui)
                        
        super(LogTracer, self).__init__([
            (r"/static/(.*)", StaticFileHandler, 
                dict(path=options.templates)),
            (r"/", DashboardHandler),
            get_router(ClientConnection).route()
        ], **settings)
