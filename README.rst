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

Using ``PyPI`` package::

    sudo easy_install logfollow-server

Install from source::

    git clone git@github.com:kachayev/logfollow.git 
    sudo python setup.py install
    sudo python setup.py upload_scripts

Launch
------

Start HTTP server::

    logfollowd.py

By default ``logfollowd.py`` server will listen 8001 port, by use can 
specify other port with ``--port`` param. Full list of launching params,
you can find in help message::

    %> logfollowd.py --help
    Usage: /usr/local/bin/logfollowd.py [OPTIONS]

    Options:
      --help                           show this help information
      --logging=debug|info|warning|error|none Set the log level. 
      --debug                          
      --gateway_host                   
      --gateway_port                   
      --host                           
      --port                           
      --templates                      

In order to use util without internet connection you have to upload all 
necessary JS libraries from CDNs. This can be done::

    logfollowctl.py upload_scripts

Supervisor
----------

`Supervisor <http://supervisord.org/>`_ can help you with relaunching Logfollow server after critical error and 
system reboot. It also provide you with simple console and web-based monitoring 
tool for checking server status, reading logs tail and restarting process remotely.

You can find more information in Supervisor documentation. Firstly, you should
setup Supervisor and ensure that supervisord daemon in already running::

    sudo -s 
    ## Generate configuration
    logfollowctl.py supervisor_config /etc/supervisor/conf.d/logfollowd.conf
    
    ## Restart supervisor in order to spawn new config file
    supervisorctl reload

    ## Check results...
    supervisorctl status logfollowd
        logfollowd                       RUNNING    pid 5390, uptime 0:00:13

You can also provide list of params for `logfollowd.py` launching calling `logfollowctl.py` util::

    logfollowctl.py supervisor_config --logging=debug --port=8001 --host=127.0.0.1

Note that, if don't use `*.conf` filename as first param after `supervisor_config` 
generated configuration will be pushed to STDOUT. It can be useful for debuging configuration 
file and for using in pipes. 


Contributors
------------

- `Alexey S. Kachayev <https://github.com/kachayev>`_
- `Vitaliy Vilyay <https://github.com/VitalVil>`_

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
See `license <https://github.com/kachayev/logfollow/blob/master/LICENSE>`_ in source code.