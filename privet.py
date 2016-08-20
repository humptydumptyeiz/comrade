from autobahn.twisted.websocket import WebSocketServerFactory

from twisted.application import service
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.static import File
from twisted.python import usage

from bouquet.http.server.root import Root
from bouquet.websocket.server.protocol import WSServerProtocol
from utils import defaults as CONST
from utils.logging import Logasun
from utils.decorators import set_log_namespace


master_log_dict = {}

class Options(usage.Options):

    optParameters = [
        ['http-port', 'h', CONST.HTTP_SERVER_PORT, 'HTTP Server Port', lambda x: int(x)],
    ]


class ComradeService(service.Service):

    def __init__(self, http_port, ws_port):
        self.http_port = http_port
        self.ws_port = ws_port
        self.ports = []
        self.log = Logasun('primary').log
        global master_log_dict
        self.master_log_dict = master_log_dict
        self.master_log_dict['primary'] = self.log

    @set_log_namespace
    def startService(self):

        factory = WebSocketServerFactory('ws://localhost:%s/stream' % self.ws_port)
        factory.protocol = WSServerProtocol
        factory.clients = []
        try:
            self.ports.append(reactor.listenTCP(self.ws_port, factory))
        except Exception as e:
            self.log.error('Exception in starting ws server')
            self.log.error(e)
            return self.stopService()
        else:
            self.log.debug('WS Server Started')
            print 'WS Server Started'

        http_server_log = Logasun('http_server').log
        self.master_log_dict['http_server'] = http_server_log
        root = Root(http_server_log)
        root.ws_clients = factory.clients
        factory = Site(root)
        try:
            self.ports.append(reactor.listenTCP(self.http_port, factory))
        except Exception as e:
            self.log.error('Exception in starting http server')
            self.log.error(e)
            return self.stopService()
        else:
            self.log.debug('HTTP SERVER STARTED')
            print 'HTTP SERVER STARTED'


        resource = File(CONST.STATIC_FOLDER)
        factory = Site(resource)
        try:
            self.ports.append(reactor.listenTCP(8000, factory))
        except Exception as e:
            print 'Exception in serving STATIC'
            self.log.error('Exception in serving STATIC')
            self.log.error(e)
            return self.stopService()
        else:
            self.log.debug('STATIC is served')
            print 'STATIC is served'


    @set_log_namespace
    def stopService(self):
        print 'Stopping all servers'
        self.log.error('Stopping all servers')
        for port in self.ports:
            try:
                port.stopListening()
            except:
                pass

def close_logs():
    print 'global close logs'
    global  master_log_dict
    for key, log in master_log_dict.items():
        print log
        try:
            log.debug('Closing log %s' % key)
            log.observer._outFile.close()
        except KeyError:
            continue

reactor.addSystemEventTrigger('after', 'shutdown', close_logs)

if __name__ == '__main__':
    import sys
    try:
        http_port = int(sys.argv[1])
    except:
        print 'HTTP-PORT: 9996'
        http_port = 9996
    try:
        ws_port = int(sys.argv[2])
    except:
        print 'WS-PORT: 9999'
        ws_port = 9999

    s = ComradeService(http_port, ws_port)
    s.startService()
    reactor.run()