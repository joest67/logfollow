"""Additional commands for setuptools script"""

import os 
import os.path

from distutils.core import Command

STATIC_DIR = '/var/logfollow'
static = lambda type_, file_: os.path.join(STATIC_DIR, type_, file_)

class StaticFilesUploader(Command):
    """Setuptools command for working with JS and CSS scripts"""
    
    scripts = [
        ('jQuery 1.6.4', 
         'https://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js', 
         'jquery.min.js'),
        ('SockJS', 
         'http://cdn.sockjs.org/sockjs-0.1.2.min.js', 
         'sockjs.js'),
        ('Knockout 1.2.1',
         'https://github.com/downloads/SteveSanderson/knockout/knockout-1.2.1.js',
         'knockout-1.2.1.js'),
        ('jQuery Tmpl',
         'https://github.com/downloads/SteveSanderson/knockout/jquery.tmpl.js',
         'jquery.tmpl.js'),
        ('Knockout Mapping',
         'https://raw.github.com/SteveSanderson/knockout.mapping/2.0.1/build/knockout.mapping.js',
         'knockout.mapping.js'),
        ('Isotope',
         'https://raw.github.com/desandro/isotope/master/jquery.isotope.min.js',
         'jquery.isotope.js')
    ]
    
    description = "Upload necessary JS and CSS scripts from CDN"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Wrapper function for calling from distutils installer"""
        self.__class__.upload()
    
    @classmethod
    def upload(cls):
        """Upload scripts and styles to local directory"""
        for script in cls.scripts:
            print 'Uploading %s ...' % script[0]
            os.system('wget -O %s - %s' % (static('js', script[2]), script[1]))
