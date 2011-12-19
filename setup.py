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

try:
    license = open('LICENSE').read()
except:
    license = None

try:
    readme = open('README.rst').read()
except:
    readme = None

setup(
    name='logfollow-server',
    version='0.0.7',
    description='Real-time Web Monitor for your logs',
    long_description=readme,
    license=license,
    url='https://github.com/kachayev/logfollow',
    author='Alexey S. Kachayev',
    author_email='kachayev@gmail.com',
    dependency_links = [
        'https://github.com/MrJoes/sockjs-tornado/zipball/master#egg=sockjs-tornado-0.0.1'
    ],
    install_requires=[
        'tornado>=2.1.1',
        'sockjs-tornado>=0.0.1'
    ],
    packages=[
        'logfollow'
    ],
    scripts=[
        'bin/logfollowd.py', 
        'bin/logfollowctl.py'
    ],
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
    },
    classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Unix',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Software Distribution',
          'Topic :: System :: Systems Administration',
    ]
)