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
        log: <path>,
        status: 'OK' or 'ERROR',
        description: 'Status description'
    }

    {
        type: 'entry',
        log: <path>,
        entries: [ 'entry 1', 'entry 2', .. ]
    }
