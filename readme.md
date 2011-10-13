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

### Messaging protocol

Client -> Server (JSON)

    {
        command: 'follow',
        logs: [<path>, <path>, ..]
    }

    {
        command: 'unfollow',
        logs: [<path>, <path>, ..]
    }

Server -> Client (JSON)

    {
        type: 'status',
        status: { <path>: 'OK', <path>: 'ERROR', ... },
        description: { <path>: 'Description', <path>: 'Description', ... }
    }

    {
        type: 'entry',
        entries: { <path>: [ 'entry 1', 'entry 2', .. ] }
    }
