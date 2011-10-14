window.onload = function(){
    var log = document.getElementById('log');
    var socket = new io.Socket(window.location.hostname, {
        port: 8001,
        rememberTransport: false
    });

    // register client
    socket.addEvent('connect', function(e) {
        socket.send({'command': 'follow', 'logs': ['/var/log/nginx/access.log']})
    });

    socket.connect();
    socket.addEvent('message', function(data) {
      console.log(data);
    });
};

