Logfollow server
================

Real-time web based monitor for your logs.

Features
--------

(Screenshots are coming...)

- Real-time updates with WebSocket or other available transports
- Easy managable screens and logs, drag-&-drop interface
- Listening logs on remote servers
- Working with directory listings
- Export/import configuration (in progress)
- Log entries filtering, duplication detect (in progress)

Install
-------

Using ``PyPI`` package

    sudo easy_install logfollow-server

Install from source

    # get the sources
    git clone git@github.com:kachayev/logfollow.git 
    sudo python setup.py install
    sudo python setup.py upload_scripts

Launch
------

Start HTTP server:

    logfollowd.py

By default ``logfollowd.py`` server will listen 8001 port, by use can 
specify other port with ``--port`` param. Full list of launching params,
you can find in help message:

    logfollowd.py --help

In order to use util without internet connection you have to upload all 
necessary JS libraries from CDNs. This can be done:

    logfollowctl.py upload_scripts

Running under `supervisor<http://supervisord.org/>`:

TBD

Contributors
------------

- `Alexey S. Kachayev<https://github.com/kachayev>`_
- `Vitaliy Vilyay<https://github.com/VitalVil>`_

TODO
----

1. Upgrade UI
2. Documentation and presentation site 
3. Export/import of client-side configurations
4. Filter and aggregation on client side 
5. Configuration and customization facilities both from client and with config 
6. Cross-platform log's listener implementation for both Linux and Mac OS
   
License 
-------

Licensed under the Apache 2.0 License. 
See `license<https://github.com/kachayev/logfollow/blob/master/LICENSE>`_ in source code.