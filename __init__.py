from os import environ
if environ['XDG_SESSION_TYPE'] == 'wayland':
    from .Wayland.edmcoverlay import Overlay
else:
    from .X11._edmcoverlay import *
    from .X11 import _edmcoverlay as edmcoverlay
