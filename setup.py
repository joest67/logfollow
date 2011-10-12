#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError, e:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='logfollow',
    version='0.0.1',
    description='Web monitor for server logs',
    author='Alexey S. Kachayev',
    author_email='kachayev@gmail.com',
    dependency_links = [],
    install_requires=[
        'tornado==2.1.1',
        'tornadio'
    ],
    packages=[
    ],
    scripts=[
        'bin/logfollow.py',
    ],
    data_files = [
        ('/etc/logfollow', ['templates/console.html']),
    ],
    include_package_data=True
)

