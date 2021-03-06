'use strict';

var ws = new WebSocket("wss://" + location.host + ":443/wss");

$(function () {
  $('form').submit(function(){
    var $this = $(this);
     ws.onopen = function() {
       console.log('sent message: %s', $('#m').val());
     };
    ws.send('{"text":"'+$('#m').val()+'"}');
    $('#m').val('');
    return false;
  });
  ws.onmessage = function(msg){
    if (msg.data.split(":")[0]=="tick") {
      ws.send("tack");
      return
    }
    var resp = JSON.parse(msg.data);

    $('#messages')
      .append($('<li>')
      .append($('<span class="message">').text(resp.text)));
  };
  ws.onerror = function(err){
    console.log("err", err);
  };
  ws.onclose = function close() {
    console.log('disconnected');
  };
});
