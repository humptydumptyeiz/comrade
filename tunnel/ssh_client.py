import os, getpass

from twisted.python.filepath import FilePath
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import UNIXClientEndpoint
from twisted.conch.ssh.keys import EncryptedKeyError, Key
from twisted.conch.client.knownhosts import KnownHostsFile
from twisted.conch.endpoints import SSHCommandClientEndpoint

from utils.logging import Logasun


log = Logasun('tunnel').log


class ClientProtocol(Protocol):

    def connectionMade(self):
        self.finished = Deferred()
        # self.sendCommand()
        self.data = ''

    def sendCommand(self):
        if self.factory.commands:
            self.transport.write(self.factory.commands.pop() + '\n')
        else:
            self.factory.loseConnection()

    def dataReceived(self, data):
        self.data += data
        print data
        for client in self.factory.ws_clients:
            print 'sending: ', data
            client.sendMessage(data)

    def connectionLost(self, reason):
        self.factory.log.debug('Connection to remote shell lost')
        self.factory.log.debug(reason)
        self.finished.callback(self.data)


def readKey(path):
    try:
        return Key.fromFile(path)
    except EncryptedKeyError:
        passphrase = getpass.getpass('%r keyphrase: ' % path)
        return Key.fromFile(path, passphrase=passphrase)


class ConnectionParameters(object):
    def __init__(self, reactor, host, port, username, password, keys,
                 knownHosts, agent):
        self.reactor = reactor
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.keys = keys
        self.knownHosts = knownHosts
        self.agent = agent

    @classmethod
    def from_without(cls, reactor, **kwargs):
        keys = []
        if kwargs.get('identity'):
            keyPath = os.path.expanduser(kwargs['identity'])
            if os.path.exists(keyPath):
                keys.append(readKey(keyPath))
        knownHostsPath = FilePath(os.path.expanduser(kwargs["knownhosts"]))
        if knownHostsPath.exists():
            knownHosts = KnownHostsFile.fromPath(knownHostsPath)
        else:
            knownHosts = None
        if kwargs["no_agent"] or "SSH_AUTH_SOCK" not in os.environ:
            agentEndpoint = None
        else:
            agentEndpoint = UNIXClientEndpoint(
                reactor, os.environ["SSH_AUTH_SOCK"])
        return cls(
            reactor, kwargs["host"], kwargs["port"],
            kwargs["username"], kwargs["password"], keys,
            knownHosts, agentEndpoint)

    def endpointForCommand(self, command):
        return SSHCommandClientEndpoint.newConnection(
            self.reactor, command, self.username, self.host,
            port=self.port, keys=self.keys, password=self.password,
            agentEndpoint=self.agent, knownHosts=self.knownHosts)

def tunnel(command, ws_clients, **kwargs):
    from twisted.internet import reactor
    global log
    parameters = ConnectionParameters.from_without(reactor, **kwargs)
    endpoint = parameters.endpointForCommand(b'%s' % command)
    factory = Factory()
    factory.protocol = ClientProtocol
    factory.log = log
    factory.ws_clients = ws_clients
    d = endpoint.connect(factory)
    d.addCallback(lambda proto: proto.finished)
    return d