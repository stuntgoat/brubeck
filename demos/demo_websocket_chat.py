
import sys
import logging
import os
from brubeck.request_handling import Brubeck, WebMessageHandler
from brubeck.connections import Mongrel2Connection
from brubeck.queryset import DictQueryset
import datetime


from ws4py.framing import Frame, \
    OPCODE_CONTINUATION, OPCODE_TEXT, \
    OPCODE_BINARY, OPCODE_CLOSE, OPCODE_PING, OPCODE_PONG

PAGE = """<html><head><script> var input = document.getElementById('input');
var chatWindow = document.getElementById('chatwindow');
var ws;
var updateChat = function (text) {
    var chatWindow = document.getElementById('chatwindow');
    chatWindow.innerHTML += "<br>" + text;
}

function connect() {
    ws = new WebSocket("ws://localhost:6767/chatsocket");
    ws.onopen = function () { 
        updateChat("Connected!");
        var button = document.getElementById('button');
        button.value = 'send';
        button.onclick = send;
    }
    ws.onmessage = function (evt) {
        updateChat(evt.data);        
    }
    ws.onclose = function (evt) {
        updateChat("closed connection");        
        var button = document.getElementById('button');
        button.value = 'connect';
        button.onclick = this;
    }
};

var send = function (elem) {
    var input = document.getElementById('input');
    ws.send(input.value);
};
</script>
</head>
<body>

<input type="text" id="input" onsubmit="send(elem);" /><input type="SUBMIT" value="connect" onclick="connect();" id="button"/>

<div id="chatwindow"></div>

</body>
</html>
"""

CLIENTS = []

class DisplayChatPage(WebMessageHandler):
    def get(self):
        self.set_body(PAGE)
        return self.render()


class WebsocketHandler(WebMessageHandler):
    def websocket(self):

        try:
            if self.message.conn_id not in CLIENTS:
                CLIENTS.append(self.message.conn_id)
            elif self.message.headers['FLAGS'] == '0x88': # close flag
                CLIENTS.pop(CLIENTS.index(self.message.conn_id))
        except KeyError:
            pass

        def ws_message(data):
            return Frame(opcode=OPCODE_TEXT, body=data, masking_key=os.urandom(4), fin=1).build()

        [self.application.msg_conn.send(self.application.msg_conn.sender_id, sender, ws_message(self.message.body)) for sender in CLIENTS]

        return Frame(opcode=OPCODE_TEXT, masking_key=os.urandom(4), fin=1).build()


config = {
    'msg_conn': Mongrel2Connection('tcp://127.0.0.1:9999', 'tcp://127.0.0.1:9998'),
    'handler_tuples': [(r'^/chatsocket', WebsocketHandler),
                       (r'^/', DisplayChatPage)],
                       
}
app = Brubeck(**config)
app.run()
