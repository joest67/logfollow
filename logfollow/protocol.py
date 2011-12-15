"""Abstractions for handling and processing client/server messages"""

import time

from tornado.escape import json_encode

class Message:
    """Namespace for specification of different messages"""

    class Jsonable(object):
        """Generate string representation of object with using JSON 
        represenration of __dict__ attr of objects' instance"""

        def __str__(self):
            return json_encode(self.__dict__)
    
    class FollowOk(Jsonable):
        """Represenration for message about following log tail"""

        __slots__ = ('type', 'log', 'status')
    
        def __init__(self, path):
            self.__dict__ = dict(type = 'status', log = path, status = 'OK')

    class FollowError(Jsonable):
        """Represenration for message about error when trying to follow log"""

        __slots__ = ('type', 'log', 'status', 'description')
    
        def __init__(self, path, reason):
            self.__dict__ = dict(type = 'status', log = path, status = 'ERROR', 
                                 description = str(reason))

    class LogEntry(Jsonable):
        """Represenration for message with log entries"""

        __slots__ = ('type', 'entries', 'log', 'time')

        def __init__(self, log, entries):
            self.__dict__ = dict(type = 'entry', log = str(log), 
                                 entries = map(str, list(entries)), 
                                 time=time.time())

        