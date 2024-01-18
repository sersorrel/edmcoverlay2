#!/usr/bin/env python
import logging
from pathlib import Path
import threading

from math import pi

# For GTK4 Layer Shell to get linked before libwayland-client we must explicitly load it before importing with gi
from ctypes import CDLL
CDLL('libgtk4-layer-shell.so')

import cairo
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version('Gtk4LayerShell', '1.0')

from gi.repository import Gtk, Gdk, GLib, Gio
from gi.repository import Gtk4LayerShell as LayerShell

from messages import Messages
from renderer import MessageRenderer

class WaylandOverlayWindow(object):
    def __init__(self, app: Gtk.Application, width: int, height: int):
        self._width = width
        self._height = height
        self._app = app
        self._app.connect('activate', self._populate_widgets_on_activate)
        self._renderer = MessageRenderer()

    @property
    def messages(self):
        return self._messages

    @messages.setter
    def messages(self, messages: Messages):
        self._messages = messages
        
    def close(self):
        self._window.close()
        
    def _populate_widgets_on_activate(self, app):
        css_provider = Gtk.CssProvider.new()
        css_provider.load_from_file(Gio.File.new_for_path(bytes(Path(__file__).resolve().parent / 'overlay.css')))
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
        self._window = Gtk.Window(application=app)
        self._window.set_default_size(self._width, self._height)
        self._window.connect('realize', self._disable_input_on_realize)

        LayerShell.init_for_window(self._window)
        LayerShell.set_layer(self._window, LayerShell.Layer.OVERLAY)
        LayerShell.set_anchor(self._window, LayerShell.Edge.LEFT, True)

        #probably useless but might be handy in the future
        self._main_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self._window.set_child(self._main_box)

        self._drawing = Gtk.DrawingArea()
        self._drawing.set_size_request(self._width, self._height)
        self._drawing.set_draw_func(self._draw)
        self._main_box.prepend(self._drawing)

        # Tell the drawing area to render
        self._drawing.queue_draw()

        # # might be handy for debugging in the future
        # self._button = Gtk.Button(label="Close")
        # self._button.connect('clicked', lambda x: self._window.close())
        # self._main_box.append(self._button)
        
        self._window.present()

        GLib.timeout_add(1000 / 2, self.refresh_screen)

    def _disable_input_on_realize(self, widget):
        #default RectangleInt is (0, 0, 0, 0)
        region = cairo.Region(cairo.RectangleInt())
        surface = self._window.get_surface()
        surface.set_input_region(region)
        
    def refresh_screen(self):
        logging.debug('refresh fired')
        self._drawing.queue_draw()
        return True
    
    def _draw(self, da: Gtk.DrawingArea, ctx: cairo.Context, width, height):
        logging.debug('drawing')
        logging.debug(f'# of msgs: {len(list(self._messages.get_messages()))}')
        for message in self._messages.get_messages():
            logging.debug(f'messages lock state: {self._messages._msg_lock}')
            self._renderer.draw_message(ctx, message)
        logging.debug(f'messages lock state: {self._messages._msg_lock}')
