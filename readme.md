### Description

Simple web based monitor for server logs

### Install

    # get the sources
    sudo python setup.py install

### Launch

Start HTTP server:

    logfollow.py --logging=debug --port=9089

Follow log file:

    tail -f <LOG_PATH> -v | nc 127.0.0.1 6777
