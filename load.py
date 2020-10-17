"""Totally definitely EDMCOverlay."""

from pathlib import Path
from subprocess import Popen

import plug

print("edmcoverlay2: loading plugin, importing lib")
import edmcoverlay
print("edmcoverlay2: got lib:", repr(edmcoverlay))
import edmcoverlay._edmcoverlay
print("edmcoverlay2: got internal lib:", repr(edmcoverlay._edmcoverlay))

overlay_process: Popen = None


def find_overlay_binary() -> Path:
    our_directory = Path(__file__).resolve().parent
    overlay_binary = our_directory / "overlay"
    if not overlay_binary.exists():
        plug.show_error("edmcoverlay2 unable to find overlay binary")
        raise RuntimeError("edmcoverlay2 unable to find overlay binary")
    return overlay_binary


def stop_overlay():
    global overlay_process
    if overlay_process:
        print("edmcoverlay2: stopping overlay")
        overlay_process.terminate()
        overlay_process.communicate()
        overlay_process = None
    else:
        print("edmcoverlay2: not stopping overlay, not started")


def plugin_start3(plugin_dir):
    print("edmcoverlay2: plugin start!")
    return "edmcoverlay2"


def journal_entry(cmdr, is_beta, system, station, entry, state):
    global overlay_process
    if entry["event"] in ["LoadGame", "StartUp"] and overlay_process is None:
        print("edmcoverlay2: starting overlay")
        overlay_process = Popen([find_overlay_binary()])
    elif entry["event"] == "ShutDown":
        print("edmcoverlay2: shutdown event received, stopping overlay")
        stop_overlay()


def plugin_stop():
    global overlay_process
    print("edmcoverlay2: exiting plugin")
    edmcoverlay._edmcoverlay._the_overlay._stop()
    stop_overlay()
