#!/usr/bin/env python
import argparse, os, sys
import signal
import logging
import threading

# For GTK4 Layer Shell to get linked before libwayland-client we must explicitly load it before importing with gi
from ctypes import CDLL
CDLL('libgtk4-layer-shell.so')

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from window import WaylandOverlayWindow
from socket_listener import ThreadedTCPServer, TCPStreamHandler
from messages import Messages

class Overlay(object):
    def __init__(self, application_id: str, width: int, height: int, hostname: str, port: int):
        self._application_id = application_id
        self._width = width
        self._height = height
        self._hostname = hostname
        self._port = port
        
        self._messages = Messages()
        self._app = Gtk.Application(application_id=self._application_id)
        self._overlay_window = WaylandOverlayWindow(self._app, self._width, self._height)
        self._overlay_window.messages = self._messages
    
        self._server = ThreadedTCPServer((self._hostname, self._port), TCPStreamHandler.Creator(self._messages.add_messages))

    def start(self, args=None):
        with self._server:
            server_thread = threading.Thread(target=self._server.serve_forever)
            # Exit the server thread when the main thread terminates
            server_thread.daemon = True
            server_thread.start()
            logging.info(f'Server loop running in thread: {server_thread.name}')
            self._app.run(args)
        
    def stop(self):
        self._server.shutdown()
        self._overlay_window.close()
        self._messages.stop_timer()

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'positional_parameters',
        nargs=argparse.ONE_OR_MORE,
        default=os.getcwd(),
        help='x y width height (x and y are only to maintain same interface with original EDMCOverlay. In this implementation these do nothing)',
        type=int)

    parser.add_argument(
        '-a',
        '--address',
        help='hostname to listen on',
        default='localhost')

    parser.add_argument(
        '-p',
        '--port',
        help='port to listen on',
        default=5010)

    parser.add_argument(
        '-i',
        '--id',
        help='application_id to use',
        default='edmcoverlay.overlay')

    parser.add_argument(
        '-v',
        '--verbose',
        help='print debug lines',
        action='store_true')
    
    return parser.parse_args()
        
if __name__ == '__main__':
    args = get_args()
    
    logging.basicConfig(
        format='%(levelname)s:%(filename)s:%(funcName)s:%(lineno)d:\t%(message)s|%(asctime)s',
        level=logging.DEBUG if args.verbose else logging.INFO)
    
    logging.debug(f'args: {args.id} {args.positional_parameters[2]} {args.positional_parameters[3]} {args.address} {args.port}')

    overlay = Overlay(args.id, args.positional_parameters[2], args.positional_parameters[3], args.address, args.port)

    def signal_handler(sig, frame):
        logging.info(f'edmcoverlay2: SIGINT/SIGTERM, exiting')
        overlay.stop()
    #KeyboardInterrupt
    signal.signal(signal.SIGINT, signal_handler)
    #Kill
    signal.signal(signal.SIGTERM, signal_handler)
    
    overlay.start()
