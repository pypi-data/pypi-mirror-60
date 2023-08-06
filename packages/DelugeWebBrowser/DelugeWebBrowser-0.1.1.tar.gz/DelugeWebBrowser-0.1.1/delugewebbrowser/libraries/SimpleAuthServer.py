import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
import base64
import os


def AuthHandlerLocalFactory(username, password, protocol_version=None):
    class AuthHandler(SimpleHTTPRequestHandler):
        ''' Main class to present webpages and authentication. '''
        key = base64.b64encode("{}:{}".format(username, password))

        def do_HEAD(self):
            # print "send header"
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def do_AUTHHEAD(self):
            # print "send header"
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def do_GET(self):
            ''' Present frontpage with user authentication. '''
            if self.headers.getheader('Authorization') is None:
                self.do_AUTHHEAD()
                self.wfile.write('no auth header received')
                pass
            elif self.headers.getheader('Authorization') == 'Basic ' + self.key:
                SimpleHTTPRequestHandler.do_GET(self)
                pass
            else:
                self.do_AUTHHEAD()
                self.wfile.write(self.headers.getheader('Authorization'))
                self.wfile.write('not authenticated')
                pass
    if protocol_version:
        AuthHandler.protocol_version = protocol_version
    return AuthHandler


def serve_http(username, password, port=8555, protocol_version="HTTP/1.0", directory=None):
    server_address = ('', port)
    HandlerClass = AuthHandlerLocalFactory(username=username,
                                           password=password,
                                           protocol_version=protocol_version)
    httpd = BaseHTTPServer.HTTPServer(server_address, HandlerClass)
    sa = httpd.socket.getsockname()
    print("Serving HTTP on {}. port {} ...".format(sa[0], sa[1]))
    if directory:
        os.chdir(directory)
    httpd.serve_forever()
