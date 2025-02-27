const socket = io.connect('http://localhost:5000');
socket.on('message', function(data) {
    console.log(data);
});