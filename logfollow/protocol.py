"""Abstractions for handling and processing client/server messages"""

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

