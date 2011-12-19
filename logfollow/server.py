"""Application handlers and servers"""

import os
import subprocess
import socket
import logging
import time

from datetime import datetime

from tornado import stack_context, ioloop
from tornado.netutil import TCPServer
from tornado.httpserver import HTTPServer
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.escape import json_encode, json_decode
from tornado.util import b, bytes_type
from tornado.options import options

from sockjs.tornado import SockJSRouter, SockJSConnection

from logfollow import ui
from logfollow.protocol import Message

def pipe(commands):
    """Communicate given list of process into one pipe"""
    def into(r, el):
        return subprocess.Popen(el, shell=True,
                                stdin=(r.stdout if r else None),  
                                stdout=subprocess.PIPE)    

    return reduce(into, commands, None)

class LogStreamer(object):
    """Call subprocessed for streaming logs"""

    streams = dict()

    @classmethod
    def follow(cls, path, follower):
        """Add additional follower to tail or start streamer if path is new
        
        Path can be just filepath to log or separated with ":" sign server 
        identity and filepath (on remote machine). So, both of this variants:
        /var/log/nginx/access.log and user@host:/var/log/nginx/access.log
        will be valid.

        It's also possible to use pluging prefixes in path. For ex., you 
        can specify path as "DIR /var/log/nginx" and it will add to following
        listing all log files from given directory. Full list of supported 
        plugins are defined by methods of PathResolver class or any other 
        added function/lambda to plugins dictionary.
        """
        for item in PathResolver.resolve(path):
            cls._follow_item(item, follower)

    @classmethod
    def _follow_item(cls, path, follower):
        if path in cls.streams:
            cls.streams[path]['followers'].add(follower)
        else:
            try:
                # Check file's validity to work with
                with open(path):
                    cls.streams[path] = dict(pid=cls._run(path), 
                                             restart=0,
                                             followers=set([follower]))
            except (IOError, OSError), e:
                # Send error notification to user
                follower.send(str(Message.FollowError(path, e)))
                logging.exception(e)
                return False

        # Send notification to user 
        follower.send(str(Message.FollowOk(path)))
        return True

    @classmethod
    def _run(cls, path):
        """Save subprocess PID in order to check periodicaly"""
        return pipe(cls._command(path)).pid
        
    @classmethod
    def unfollow(cls, path, follower):
        """Remove client from list of followers.

        We should keep in mind that follow/unfollow methods are
        separated in time, so we can catch error with different 
        results of resolving path on start and on finish. To 
        avoid this it's necessary to track base command and resolving
        results on following.
        """
        for item in PathResolver.resolve(path):
            cls._unfollow_item(item, follower)

    @classmethod
    def _unfollow_item(cls, path, follower):
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
            deadline = (time.time() + 
                2 ** min(cls.streams[path].get('restart', 0), 5))

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
        """Generate command for log stream run
        
        In order to retrieve log stream from remote server, we will 
        use SSH connection by given user@host pair. This will be enough 
        only in case of password-less way of connection 
        (with using ssh-key, for ex). 
        
        Auto checking of ssh keys validity or even facilities to provide 
        auth parameters from client side, will be add during next iterations.
        """
        nc = "nc {host} {port}".format(host=options.gateway_host,
                                       port=options.gateway_port)
        if not path.count(':'):
            tail = 'tail -f -v %s' % path
        else:
            tail = "ssh %s 'tail -f -v %s'" % tuple(path.split(':', 1))
                    
        logging.info('Start streaming %s with %s', path, [tail, nc])
        return tail, nc

class PathResolver(object):
    """List of plugins for resolving given path to log"""

    @staticmethod
    def dir(path):
        """Get list of files from directory given in path param.

        This plugin should ignore all files, which ends with figure
        (for ex., *.1, *.2 etc) cause of log rotating results. To support 
        hierarchy in files/directory you should rewrite this method as well.

        We should also add here method for periodical checking of new 
        files in directory (it's not always necessary, but ignoring this 
        fact can be unpredictable for users).
        """
        logs = []
        try:
            for root, dirs, files in os.walk(path):
                for log in files:
                    try:
                        int(log.split('.')[-1]) 
                    except (ValueError, IndexError):
                        logs.append(os.path.join(root, log))
        except OSError:
            # TODO: Add here something like "plugin resolving error"
            raise 
        else: 
            return logs

    @classmethod
    def resolve(cls, path):
        """Should also return iterable object"""
        if not path.count(' '):
            return [path]
        
        plugin, item = path.split(' ', 1)
        try: 
            # TODO: Possbile we will add other way to init plugin
            resolver = getattr(cls, plugin.lower())
        except AttributeError:
            return [path]
        else:
            items = resolver(item)
            return [items] if type(items) == str else items

class LogServer(TCPServer):
    """Handle incoming TCP connections from log pusher clients"""

    def handle_stream(self, stream, address):
        """Called when new IOStream object is ready for usage"""
        logging.info('Incoming connection from %r', address)
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

        self.stream.set_close_callback(self._on_disconnect)
        self.stream.read_until(b("\n"), self._on_head)


    def _on_head(self, line):
        """Extract information about log file path.

        To use this, you should call tail util with -v param.
        If you use ZMQ sockets, you can push file name with
        socket identity signiture.
        """
        line = line.strip()
        try:
            self.filepath = line.split()[1]
        except IndexError:
            self.filepath = None
            logging.error('Illegal header send to TCP server: %s', line)
            self.stream.close()
        else:
            self.__class__.logs.add(str(self))
            self.wait()

    def _on_read(self, line):
        """Called when new line received from connection"""
        ClientConnection.broadcast(Message.LogEntry(self, [line.strip()]))
        self.wait()

    def wait(self):
        """Read from stream until the next signed end of line"""
        self.stream.read_until(b("\n"), self._on_read)

    def _on_disconnect(self, *args, **kwargs):
        logging.info('Log streamer disconnected %s', self)
        try:
            self.__class__.logs.remove(str(self))
        except KeyError:
            logging.warning('Try to remove undefined log %s', self)

    def __str__(self):
        """Build string representation, will be used for working with
        server identity (not only file path) in future"""
        return str(self.filepath)

class DashboardHandler(RequestHandler):
    """Render HTML page with user's dashboard"""

    def get(self):
        self.render(
            os.path.join(self.application.options.templates, 'console.html'),
            **self.application.settings
         )
        
class ClientConnection(SockJSConnection):
    clients = set()

    def __init__(self, *args, **kwargs):
        """Initialize client connection by creating empty list of followed logs"""
        self.follow = set()
        super(ClientConnection, self).__init__(*args, **kwargs)

    @classmethod
    def broadcast(cls, message):
        """Send JSON encoded message to all connected clients"""
        logging.debug('Broadcasting: %s', message)
        for client in cls.clients:
            if message.log in client.follow:
                client.send(str(message))

    def on_open(self, request, *args, **kwargs):
        """Called when new connection from client created"""
        logging.info('Client connected: %s', self)
        self.open_request = request
        self.clients.add(self)

    def on_message(self, message):
        """Called when protocol package received from client"""
        logging.info('Received from client: %s', message)
        self._command(json_decode(message))

    def on_close(self):
        """Called when connection is closed"""
        logging.info('Client disconnected: %s', self)
        self.clients.remove(self)

    def _command(self, protocol):
        """Switch between known commands from message.
        
        Possible in future we will redesign this actions 
        with using some modern MVC-like or Command-based pattern
        for handling many different commands, but for this time 
        it's fully enough.
        """
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
                        socket_port=options.port, 
                        socket_handler=options.socket_handler,
                        ui_modules=ui)
            
        super(LogTracer, self).__init__([
            # Static files handling is necessary only for working with 
            # js/css files uploaded to local machine with using install script
            (r"/static/(.*)", StaticFileHandler, dict(path=options.templates)),
            (r"/", DashboardHandler),
        ] + SockJSRouter(ClientConnection, '/'+options.socket_handler).urls, 
        **settings)
