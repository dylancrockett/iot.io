from eventlet import websocket
from eventlet import wsgi
from eventlet.green import socket
from eventlet.support import get_errno


# custom websocket WSGI app which does not automatically send the closing frame
class CustomWebSocketWSGI(websocket.WebSocketWSGI):
    def __call__(self, environ, start_response):
        http_connection_parts = [
            part.strip()
            for part in environ.get('HTTP_CONNECTION', '').lower().split(',')]
        if not ('upgrade' in http_connection_parts and
                environ.get('HTTP_UPGRADE', '').lower() == 'websocket'):
            # need to check a few more things here for true compliance
            start_response('400 Bad Request', [('Connection', 'close')])
            return []

        try:
            if 'HTTP_SEC_WEBSOCKET_VERSION' in environ:
                ws = self._handle_hybi_request(environ)
                print("HTTP_SEC")
            elif self.support_legacy_versions:
                print("LEGACY")
                ws = self._handle_legacy_request(environ)
            else:
                raise websocket.BadRequest()
        except websocket.BadRequest as e:
            status = e.status
            body = e.body or b''
            headers = e.headers or []
            start_response(status,
                           [('Connection', 'close'), ] + headers)
            return [body]

        try:
            self.handler(ws)
        except socket.error as e:
            if get_errno(e) not in websocket.ACCEPTABLE_CLIENT_ERRORS:
                raise
        # Make sure we send the closing frame
        # ws._send_closing_frame(True)
        # use this undocumented feature of eventlet.wsgi to ensure that it
        # doesn't barf on the fact that we didn't call start_response
        return wsgi.ALREADY_HANDLED
