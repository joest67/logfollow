"""UI modules for Tornado template engine"""

import os.path
import logging

from logfollow import install
from tornado.web import UIModule

class LocalCopy(UIModule):
    """Template module to return link to local copy of file if presents"""

    def render(self, p):
        # Check local copy
        p = p.strip('/')
        if os.path.exists(install.static('', p)):
            return os.path.join('/static', p)
        
        # Check CDN link from installation script
        for script in install.StaticFilesUploader.scripts:
            if p.endswith(script[2]):
                return script[1]

        raise ValueError('Try to load unknown file: %s', p)
