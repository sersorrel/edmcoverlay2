from os import environ
if environ.get('XDG_SESSION_TYPE', 'X11') == 'wayland':
    from .Wayland import edmcoverlay
    from .Wayland.edmcoverlay import Overlay
else:
    from .X11.edmcoverlay import *
    from .X11 import edmcoverlay as edmcoverlay
