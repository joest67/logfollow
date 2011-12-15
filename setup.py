#!/usr/bin/env python

import os
import functools

here  = lambda x: os.path.join(os.path.abspath(os.path.dirname(__file__)), x)
files = lambda x: map(functools.partial(os.path.join, x), os.listdir(here(x)))

try:
    from setuptools import setup
except ImportError, e:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='logfollow-server',
    version='0.0.4',
    description='Web monitor for server logs',
    author='Alexey S. Kachayev',
    author_email='kachayev@gmail.com',
    dependency_links = [],
    install_requires=['tornado==2.1.1','tornadio'],
    packages=['logfollow'],
    scripts=['bin/logfollowd.py', 'bin/logfollowctl.py'],
    data_files = [
        ('/var/logfollow', ['templates/console.html', 
                            'templates/favicon.ico']),
        ('/var/logfollow/js', ['templates/js/app.js']),
        ('/var/logfollow/css', ['templates/css/app.css']),
        ('/var/logfollow/images', files('templates/images/'))
    ],
    include_package_data=True,
    entry_points = {
        "distutils.commands": 
            ["upload_scripts = logfollow.install:StaticFilesUploader"]
    }
)
