import logging

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
        self.draw_text(ctx, message)

    def draw_text(self, ctx: cairo.Context, message: dict):
        self._draw_text(ctx, message['size'], message['color'], message['text'], message['x'], message['y'])

    def _draw_text(self, ctx: cairo.Context, fontsize: str, fontcolor: str, text: str, x: int, y: int):
        if not text:
            return

        size = self._normal_font
        if fontsize:
            size = self._font_sizes.get(fontsize, self._normal_font)

        rgba = self._get_color(fontcolor)
        if rgba:
            logging.debug(f'text draw color: {rgba.red} {rgba.green} {rgba.blue} {rgba.alpha}')
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
    
    # def draw_marker(self, ctx: cairo.Context, message: dict):
    #     if not marker.Color:
    #         return

    #     brush = self._get_color(marker.Color)
    #     if not brush:
    #         return

    #     ctx.set_source(brush)
    #     ctx.set_line_width(1.0)

    #     if marker.Marker == 'cross':
    #         # draw 2 lines
    #         ctx.move_to(marker.X - 3, marker.Y - 3)
    #         ctx.line_to(marker.X + 3, marker.Y + 3)
    #         ctx.stroke()

    #         ctx.move_to(marker.X + 3, marker.Y - 3)
    #         ctx.line_to(marker.X - 3, marker.Y + 3)
    #         ctx.stroke()

    #     elif marker.Marker == 'circle':
    #         circle_bounds = (marker.X - 4, marker.Y - 4, 8, 8)
    #         ctx.arc(circle_bounds[0] + circle_bounds[2] / 2, circle_bounds[1] + circle_bounds[3] / 2,
    #                min(circle_bounds[2], circle_bounds[3]) / 2, 0, 2 * 3.14159)
    #         ctx.stroke()

    # def draw_vector_line(self, brush, start, end, ctx):
    #     if not brush:
    #         return

    #     ctx.set_source(brush)
    #     ctx.set_line_width(1.0)
    #     ctx.move_to(start.X, start.Y)
    #     ctx.line_to(end.X, end.Y)
    #     ctx.stroke()

    # def draw_vector(self, start, erase, ctx):
    #     # draw first point
    #     if not start.Vector or len(start.Vector) < 1:
    #         return

    #     last = start.Vector[0]

    #     for current in start.Vector[1:]:
    #         brush = self._get_color(start.Color)
    #         self.draw_vector_line(brush, last, current, ctx)
    #         self.draw_marker(last, ctx)
    #         self._draw_text_ex('normal', last.Color, last.Text, last.X + 2, last.Y + 7, ctx)
    #         last = current

    #     # draw last marker
    #     self.draw_marker(last, ctx)
    #     self._draw_text_ex('normal', last.Color, last.Text, last.X + 2, last.Y + 7, ctx)

    # def draw_shape(self, g, ctx):
    #     if g.Shape == 'rect':
    #         rect_bounds = (g.X, g.Y, g.W, g.H)
    #         fill = self._get_color(g.Fill)
    #         if fill:
    #             ctx.set_source(fill)
    #             ctx.rectangle(rect_bounds[0], rect_bounds[1], rect_bounds[2], rect_bounds[3])
    #             ctx.fill_preserve()

    #         rgba = self._get_color(g.Color)
    #         if rgba:
    #             ctx.set_source(rgba)
    #             ctx.set_line_width(1.0)
    #             ctx.rectangle(rect_bounds[0], rect_bounds[1], rect_bounds[2], rect_bounds[3])
    #             ctx.stroke()

    #     elif g.Shape == 'vect':
    #         self.draw_vector(g, False, ctx)

    def _get_color(self, color):
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
