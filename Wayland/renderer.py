import logging

from math import pi

import cairo
import gi
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Pango, PangoCairo, Gdk

class MessageRenderer(object):
    def __init__(self):
        self._font_sizes = {
            'large': Pango.font_description_from_string('Sans Bold 19'),
            'normal': Pango.font_description_from_string('Sans 12'),
        }
        self._normal_font = Pango.FontDescription.from_string('Sans 12')
        
        self._colors = {
            'red': Gdk.RGBA(),
            'yellow': Gdk.RGBA(),
            'green': Gdk.RGBA(),
            'blue': Gdk.RGBA(),
            'black': Gdk.RGBA(),
        }
        self._colors['red'].parse('#ff0000')
        self._colors['yellow'].parse('#ffff00')
        self._colors['green'].parse('#00ff00')
        self._colors['blue'].parse('#0000ff')
        self._colors['black'].parse('#000000')

    def draw_message(self, ctx: cairo.Context, message: dict):
        if 'shape' in message:
            self._draw_shape(
                ctx,
                message)
        if 'marker' in message:
            self.draw_marker(
                ctx,
                message['color'],
                message['marker'],
                message['x'],
                message['y'])
        if 'text' in message:
            self._draw_text(
                ctx,
                message)

    def _draw_text(self, ctx: cairo.Context, message: dict):
        self.draw_text(ctx, message['size'], message['color'], message['text'], message['x'], message['y'])

    def _draw_shape(self, ctx: cairo.Context, message: dict):
        if message['shape'] == 'rect':
            self.draw_rectangle(
                ctx,
                message.get('color', None),
                message.get('fill', None),
                message['x'],
                message['y'],
                message['w'],
                message['h'])
        elif message['shape'] == 'vect':
            self.draw_vector(
                ctx,
                message.get('color', 'green'),
                message['vector'])
        else:
            logging.error(f'unknown shape: {message}')
    
    def draw_text(self, ctx: cairo.Context, fontsize: str, fontcolor: str, text: str, x: int, y: int):
        if not text:
            return

        size = self._normal_font
        if fontsize:
            size = self._font_sizes.get(fontsize, self._normal_font)

        rgba = self._get_color(fontcolor)
        if rgba:
            logging.debug(f'color: {rgba.red} {rgba.green} {rgba.blue} {rgba.alpha}')
            ctx.set_source_rgba(rgba.red, rgba.green, rgba.blue, rgba.alpha)
        else:
            ctx.set_source_rgba(0, 1, 0, 1)
        ctx.set_font_size(size.get_size() / Pango.SCALE)
        # this creates separate pango context for each layout. Might be too slow
        layout = PangoCairo.create_layout(ctx)
        layout.set_text(text)
        layout.set_font_description(size)
        ctx.move_to(x, y)
        PangoCairo.show_layout(ctx, layout)

    def draw_rectangle(self, ctx: cairo.Context, color: str, fill: str, x: int, y: int, width: int, height: int):
        rgba = self._get_color(color)
        if rgba:
            logging.debug(f'color: {rgba.red} {rgba.green} {rgba.blue} {rgba.alpha}')
            ctx.set_source_rgba(rgba.red, rgba.green, rgba.blue, rgba.alpha)
            ctx.rectangle(x, y, width, height)
            ctx.stroke()

        rgba = self._get_color(fill)
        if rgba:
            logging.debug(f'fill: {rgba.red} {rgba.green} {rgba.blue} {rgba.alpha}')
            ctx.set_source_rgba(rgba.red, rgba.green, rgba.blue, rgba.alpha)
            ctx.set_line_width(1)
            ctx.rectangle(x, y, width, height)
            ctx.fill()

    #remember that vector point can include marker and text 
    def draw_vector(self, ctx: cairo.Context, color: str, points: list):
        if not points:
            return

        ctx.move_to(points[0]['x'], points[0]['y'])

        rgba = self._get_color(color)
        if rgba:
            logging.debug(f'color: {rgba.red} {rgba.green} {rgba.blue} {rgba.alpha}')
            ctx.set_source_rgba(rgba.red, rgba.green, rgba.blue, rgba.alpha)
        else:
            logging.error(f'no color: {rgba.red} {rgba.green} {rgba.blue} {rgba.alpha}')
            ctx.set_source_rgba(0, 1, 0, 1)

        for point in points:
            ctx.line_to(point['x'], point['y'])
            
            if 'marker' in point:
                ctx.save()
                self.draw_marker(
                    ctx,
                    point.get('color', color),
                    point['marker'],
                    point['x']+2,
                    point['y']+7)
                ctx.restore()
            if 'text' in point:
                ctx.save()
                self.draw_text(
                    ctx,
                    "normal",
                    point.get('color', color),
                    point['text'],
                    point['x']+2,
                    point['y']+7)
                ctx.restore()
        # inside the loop?
        ctx.stroke()

    def draw_marker(self, ctx: cairo.Context, color: str, marker:str, x: int, y: int):
        if not color:
            return
        
        rgba = self._get_color(color)
        if rgba:
            logging.debug(f'color: {rgba.red} {rgba.green} {rgba.blue} {rgba.alpha}')
            ctx.set_source_rgba(rgba.red, rgba.green, rgba.blue, rgba.alpha)
        else:
            ctx.set_source_rgba(0, 1, 0, 1)

        ctx.set_line_width(1.0)

        if marker == 'cross':
            ctx.move_to(x-3, y-3)
            ctx.line_to(x+3, y+3)
            
            ctx.move_to(x+3, y-3)
            ctx.line_to(x-3, y+3)
            ctx.stroke()
        elif marker == 'circle':
            ctx.arc(x, y, 8, 0, 2*pi)
            ctx.stroke()
        else:
            logging.error(f'unknown marker: {marker}')

    def _get_color(self, color):
        if color is None or color == '' or color == '#':
            return None
        
        rgba = self._colors.get(color)
        if not rgba:
            try:
                rgba = Gdk.RGBA()
                rgba.parse(color)
                self._colors[color] = rgba
            except Exception as e:
                logging.error(f' renderer color error for {color}: {e}')
                rgba.parse('green')
        return rgba
