import socket
import threading
import socketserver
import logging
import json

class TCPStreamHandler(socketserver.StreamRequestHandler):
    def __init__(self, request, client_address, server, func=None):
        self.func = func
        super().__init__(request, client_address, server)

    @classmethod
    def Creator(cls, *args, **kwargs):
        def _HandlerCreator(request, client_address, server):
            cls(request, client_address, server, *args, **kwargs)
        return _HandlerCreator

    def handle(self):
        lines = []
        while self.rfile.peek():
            self.data = self.rfile.readline().strip()
            if self.data:
                logging.debug(json.loads(self.data))
            lines.append(json.loads(self.data))
        if self.func is not None:
            self.func(lines)
    
class MyTCPHandler(socketserver.StreamRequestHandler):
    """
    The request handler class for debugging.
    """
    def handle(self):
        while self.rfile.peek():
            self.data = self.rfile.readline().strip()
            logging.info(f'{self.client_address[0]} wrote:')
            logging.info(json.loads(self.data))

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:%(lineno)d:\t%(message)s', level=logging.INFO)
    server = ThreadedTCPServer(('localhost', 5010), MyTCPHandler)
    with server:
        ip, port = server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        logging.info(f'Server loop running in thread: {server_thread.name}')
        while True:
            pass
