from autobahn.twisted.websocket import WebSocketServerProtocol


class WSServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print request.peer
        self.factory.clients.append(self)

    def onOpen(self):
        print 'WS Server open'

    def onMessage(self, payload, isBinary):
        if not isBinary:
            print 'Received: ', payload.decode('utf8')

