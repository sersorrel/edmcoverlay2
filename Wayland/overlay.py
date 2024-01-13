#!/usr/bin/env python
import configparser
import signal, sys
import logging

# For GTK4 Layer Shell to get linked before libwayland-client we must explicitly load it before importing with gi
from ctypes import CDLL
CDLL('libgtk4-layer-shell.so')

import gi
gi.require_version("Gtk", "4.0")
gi.require_version('Gtk4LayerShell', '1.0')

from gi.repository import Gtk
from gi.repository import Gtk4LayerShell as LayerShell



class WaylandOverlay(object):
    def __init__(self, app: Gtk.Application, width: int, height: int):
        self._width = width
        self._height = height
        self._app = app
        self._app.connect('activate', self.on_activate)

    def on_activate(self, app):
        self._window = Gtk.Window(application=app)
        self._window.set_default_size(self._width, self._height)

        LayerShell.init_for_window(self._window)
        LayerShell.set_layer(self._window, LayerShell.Layer.OVERLAY)
        LayerShell.set_anchor(self._window, LayerShell.Edge.LEFT, True)

        #probably useless but might be handy in the future
        self._main_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)
        self._window.set_child(self._main_box)

        self._drawing = Gtk.DrawingArea()
        self._drawing.set_size_request(self._width, self._height)
        self._drawing.set_opacity(0)
        self._main_box.prepend(self._drawing)

        #might be handy for debugging in the future
        # self._button = Gtk.Button(label="Close")
        # self._button.connect('clicked', lambda x: self._window.close())
        # self._main_box.append(self._button)
        
        self._window.present()

def signal_handler(sig, frame):
    logging.info(f'edmcoverlay2: SIGINT/SIGTERM, exiting')
    sys.exit(0)
    
if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(lineno)d:\t%(message)s', level=logging.INFO)
    
    app = Gtk.Application(application_id='edmcoverlay.overlay')
    overlay = WaylandOverlay(app, 800, 800)
    #KeyboardInterrupt
    signal.signal(signal.SIGINT, signal_handler)
    #Kill
    signal.signal(signal.SIGTERM, signal_handler)
    app.run(None)
