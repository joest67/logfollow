# Description

Simple web based monitor for server logs.
(Screenshots are coming..)

### Install

    # get the sources
    sudo python setup.py install

### Launch

Start HTTP server:

    logfollow.py --logging=debug --port=8001

Follow log file:

    tail -f <LOG_PATH> -v | nc 127.0.0.1 6777

After this you can open web interface http://localhost:8001/ and follow visual tips.

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
        entries: [ 'entry 1', 'entry 2', .. ],
        time: <UNIXTIMESTAMP>
    }
    
    
## License 

(The MIT License)

Copyright (c) 2011 Guillermo Rauch &lt;guillermo@learnboost.com&gt;

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
'Software'), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.    
