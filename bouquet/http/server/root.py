import json

from twisted.web.resource import Resource, NoResource
from twisted.web.server import NOT_DONE_YET

from tunnel.ssh_client import tunnel
from utils.decorators import set_log_namespace


class Root(Resource):

    def __init__(self, log):
        Resource.__init__(self)
        self.log = log
        self.ws_protocol = None

    def getChild(self, path, request):
        if path == 'command':
            return self
        else:
            return NoResource()

    @set_log_namespace
    def render_POST(self, request):
        request.setHeader('Access-Control-Allow-Origin', '*')
        print 'payload: ', request.content.getvalue()
        payload = json.loads(request.content.getvalue())

        command = str(payload.get('command', 'ls'))
        print type(command), ' ', command
        params = {}
        params['host'] = payload.get('host')
        params['port'] = int(payload.get('port', 22))
        params['username'] = str(payload.get('username'))
        params['password'] = str(payload.get('password'))
        params['knownhosts'] = str(payload.get('knownhosts', '~/.ssh/known_hosts'))
        params['no_agent'] = payload.get('no_agent', True)

        d = tunnel(command, self.ws_clients, **params)
        d.addCallbacks(self.finish_request, self.finish_request, callbackArgs=[request, 200],errbackArgs=[request, 500])

        return NOT_DONE_YET

    @set_log_namespace
    def finish_request(self, result, request, response_code):
        print result
        self.log.debug(result)
        request.setResponseCode(response_code)
        request.write(str(result))
        request.finish()

