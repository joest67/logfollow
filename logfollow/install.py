from os import system, path
from distutils.core import Command

STATIC_DIR = '/var/logfollow'
static = lambda type_, file_: path.join(STATIC_DIR, type_, file_)

class StaticFilesUploader(Command):
    """Setuptools command for working with JS and CSS scripts"""
    
    scripts = [
        ('jQuery 1.6.4', 
         'https://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js', 
         'jquery.min.js'),
        ('Socket.io', 
         'http://cdn.socket.io/stable/socket.io.js', 
         'socket.io.js'),
        ('Knockout 1.2.1',
         'https://github.com/downloads/SteveSanderson/knockout/knockout-1.2.1.js',
         'knockout-1.2.1.js'),
        ('jQuery Tmpl',
         'https://github.com/downloads/SteveSanderson/knockout/jquery.tmpl.js',
         'jquery.tmpl.js')
    ]
    
    description = "Upload necessary JS and CSS scripts from CDN"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Upload scripts and styles to local directory"""
        for script in self.scripts:
            print 'Uploading %s ...' % script[0]
            system('wget -O %s - %s' % (static('js', script[2]), script[1]))

