window.onload = function(){
    var log = document.getElementById('log');
    var socket = new io.Socket(window.location.hostname, {
        port: 8001,
        rememberTransport: false
    });

    // register client
    socket.addEvent('connect', function(e) {
            sign = Math.floor(Math.random(1000) * 1000);
        socket.send({ id: sign });
    });

    socket.connect();
    socket.addEvent('message', function(data) {
      console.log(data);
    });
};

