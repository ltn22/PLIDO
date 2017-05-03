var path = require('path');
var express = require('express');
var util=require('util')

var httpServer = express();

httpServer.post('/coap/*', function(req, res){
    var buff = '';

    req.on('data',function(data){
	 buff = data;
      });
    req.on('end',function(){
	fromGW = JSON.parse(buff)
	console.log (util.inspect(fromGW))

	var devEUI = fromGW.devEUI

	res.writeHead(200);
	var responseStruct = {
	    'fport' : 2,
	    'data' : new Buffer("Pleased to meet you").toString("base64"),
	    'devEUI' : devEUI
	}
	console.log(responseStruct)
	
	res.end(JSON.stringify(responseStruct));
	res.end();
    });
});

httpServer.listen(3001);
console.log('Listening on port 3001');
