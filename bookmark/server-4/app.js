/**
 * server-4/app.js
 *
 * David J. Malan
 * malan@harvard.edu
 *
 * Tim Griesser
 * tgriesser@cs50.harvard.edu
 *
 * Demonstrates a chat server using socket.io.
 */

var fs = require('fs');
var express = require('express'); //use npm to install express & socket.io to IDE
var app = express();
var server = app.listen(8080); //port 1337 doesn't work in CS50 IDE
var io = require('socket.io').listen(server);

// index.html
app.get('/', function(req, res) {
    fs.createReadStream('index.html').pipe(res);
});

// sockets
io.sockets.on('connection', function(client){

    // when a message comes in from a client, re-emit it from the server to client(s)
    client.on('message:client', function(data) {
        client.broadcast.emit('message:server', {message: data.message});
    });
});
