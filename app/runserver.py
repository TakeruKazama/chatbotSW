"""
from autobahn.twisted.websocket import WebSocketServerProtocol


class MyServerProtocol(WebSocketServerProtocol):

   def onOpen(self):
     print("WebSocket connection open.")

   def onMessage(self, payload, isBinary):
      ## echo back message verbatim
      self.sendMessage(payload, isBinary)
      for c in self.factory.clients:
          c.sendMessage(payload)
      print(payload, isBinary)

if __name__ == '__main__':

   import sys

   from twisted.python import log
   from twisted.internet import reactor
   log.startLogging(sys.stdout)

   from autobahn.twisted.websocket import WebSocketServerFactory
   factory = WebSocketServerFactory()
   factory.protocol = MyServerProtocol

   reactor.listenTCP(9000, factory)
   reactor.run()
"""
import sys
import json
import re
import bot


from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol, \
    listenWS

from autobahn.twisted.resource import WebSocketResource

class BroadcastServerProtocol(WebSocketServerProtocol):

    def onOpen(self):
        self.factory.register(self)

    def onMessage(self, payload, isBinary):
        if not isBinary:
            msg = self.response(payload.decode('utf8'))
            self.factory.broadcast(msg)

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)

    def response(self, text):
        mention = ('bot', '@bot', 'bot:')
        j = json.loads(text)
        if re.split(': | |:', j['text'])[0] in mention:
            print("I'm a bot!")
            self.sendMessage(bot.bot_response(j).encode('utf8'))
        # broadcast
        return json.dumps({'success': True, 'type': 'message', 'text': j['text']})


class BroadcastServerFactory(WebSocketServerFactory):

    """
    Simple broadcast server broadcasting any message it receives to all
    currently connected clients.
    """

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        self.clients = []
        self.tickcount = 0
        #self.tick()

    def tick(self):
        self.tickcount += 1
        self.broadcast('{"text":"tick %d from server"}' % self.tickcount)
        reactor.callLater(1, self.tick)

    def register(self, client):
        if client not in self.clients:
            print("registered client {}".format(client.peer))
            self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            print("unregistered client {}".format(client.peer))
            self.clients.remove(client)

    def broadcast(self, msg):
        print("broadcasting message '{}' ..".format(msg))
        for c in self.clients:
            c.sendMessage(msg.encode('utf8'))
            print("message sent to {}".format(c.peer))


class BroadcastPreparedServerFactory(BroadcastServerFactory):

    """
    Functionally same as above, but optimized broadcast using
    prepareMessage and sendPreparedMessage.
    """

    def broadcast(self, msg):
        print("broadcasting prepared message '{}' ..".format(msg))
        preparedMsg = self.prepareMessage(msg)
        for c in self.clients:
            c.sendPreparedMessage(preparedMsg)
            print("prepared message sent to {}".format(c.peer))


if __name__ == '__main__':

    log.startLogging(sys.stdout)

    ServerFactory = BroadcastServerFactory
    # ServerFactory = BroadcastPreparedServerFactory

    bmxport = sys.argv[1]

    factory = ServerFactory("ws://0.0.0.0:"+bmxport)
    factory.protocol = BroadcastServerProtocol
    resource = WebSocketResource(factory)

    webdir = File("app")
    webdir.putChild(b"ws", resource)

    web = Site(webdir)
    reactor.listenTCP(int(bmxport), web)
    reactor.run()
