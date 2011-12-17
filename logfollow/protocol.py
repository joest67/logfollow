"""Abstractions for handling and processing client/server messages"""

import time

from tornado.escape import json_encode

class Message:
    """Namespace for specification of different messages"""

    class Jsonable(object):
        """Generate string representation of object with using JSON 
        represenration of __dict__ attr of objects' instance"""

        def __str__(self):
            attrs = dict([(k, getattr(self, k)) for k in self.__slots__])
            return json_encode(attrs)
    
    class FollowOk(Jsonable):
        """Represenration for message about following log tail"""

        __slots__ = ('type', 'log', 'status')

        def __init__(self, path):
            self.type = 'status'
            self.status = 'OK'
            self.log = path 

    class FollowError(Jsonable):
        """Represenration for message about error when trying to follow log"""

        __slots__ = ('type', 'log', 'status', 'description')
    
        def __init__(self, path, reason):
            self.type = 'status' 
            self.status = 'ERROR' 
            self.log = path 
            self.description = str(reason)

    class LogEntry(Jsonable):
        """Represenration for message with log entries"""

        __slots__ = ('type', 'entries', 'log', 'time')

        def __init__(self, log, entries):
            self.type = 'entry'
            self.log = str(log) 
            self.entries = map(str, list(entries)) 
            self.time=time.time()   

        