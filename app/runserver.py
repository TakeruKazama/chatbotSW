import sys
import json
import re
import threading
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
            th = threading.Thread(target=self.response, name="th", args=(payload.decode('utf8'), ))
            th.start()
            # self.response(payload.decode('utf8'))

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)

    def response(self, text):
        mention = ('bot', '@bot', 'bot:')
        j = json.loads(text)
        # broadcast
        self.factory.broadcast(json.dumps({'success': True, 'type': 'message', 'text': j['text']}))

        if re.split(': | |:', j['text'])[0] in mention:
            for x in bot.bot_response(j):
                self.sendMessage(x)


class BroadcastServerFactory(WebSocketServerFactory):

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        self.clients = []
        self.tickcount = 0
        # self.tick()

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

if __name__ == '__main__':

    log.startLogging(sys.stdout)

    ServerFactory = BroadcastServerFactory

    bmxport = sys.argv[1]

    factory = ServerFactory("wss://0.0.0.0:443")
    factory.protocol = BroadcastServerProtocol
    resource = WebSocketResource(factory)

    # テストに通すためwsサーバーも立てておく
    factory2 = ServerFactory("ws://0.0.0.0:80")
    factory2.protocol = BroadcastServerProtocol
    resource2 = WebSocketResource(factory2)

    webdir = File("app")
    webdir.putChild(b"wss", resource)
    webdir.putChild(b"ws", resource2)

    web = Site(webdir)
    reactor.listenTCP(int(bmxport), web)
    reactor.run()
