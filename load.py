"""Totally definitely EDMCOverlay."""

import importlib
import logging
from os import environ
from pathlib import Path
from subprocess import Popen
import tkinter as tk
from tkinter import ttk
import socket

from config import appname, config
import myNotebook as nb
import plug
from ttkHyperlinkLabel import HyperlinkLabel


plugin_name = Path(__file__).parent.name
logger = logging.getLogger(f"{appname}.{plugin_name}")


base_dir = Path(__file__).parent
logger.debug("edmcoverlay2: loading plugin, we are: %s", repr(base_dir))
edmcoverlay = importlib.import_module(base_dir.name)
logger.debug("edmcoverlay2: got lib: %s", repr(edmcoverlay))
logger.debug("edmcoverlay2: got internal lib: %s", repr(edmcoverlay.edmcoverlay))

overlay_process: Popen = None
xpos_var: tk.IntVar
ypos_var: tk.IntVar
width_var: tk.IntVar
height_var: tk.IntVar


def find_overlay_binary() -> Path:
    our_directory = Path(__file__).resolve().parent
    if environ.get('XDG_SESSION_TYPE', 'X11') == 'wayland':
        overlay_binary = our_directory / 'Wayland' / 'main.py'
    else:
        overlay_binary = our_directory / 'overlay'
    if not overlay_binary.exists():
        plug.show_error("edmcoverlay2 unable to find overlay binary")
        raise RuntimeError("edmcoverlay2 unable to find overlay binary")
    return overlay_binary


def start_overlay():
    global overlay_process

    if environ.get('XDG_SESSION_TYPE', 'X11') == 'wayland':
        overlay_already_running = False
        try:
            connection = socket.socket()
            connection.connect(('localhost', 5010))
            overlay_already_running = True
            connection.close()
        except ConnectionRefusedError:
            overlay_already_running = False
            connection.close()
        if overlay_already_running:
            overlay_process = None
            logger.info("edmcoverlay2: not starting overlay, already running")
            return
        
    if not overlay_process:
        logger.info("edmcoverlay2: starting overlay")
        xpos = config.get_int("edmcoverlay2_xpos") or 0
        ypos = config.get_int("edmcoverlay2_ypos") or 0
        width = config.get_int("edmcoverlay2_width") or 1920
        height = config.get_int("edmcoverlay2_height") or 1080
        overlay_process = Popen([find_overlay_binary(), str(xpos), str(ypos), str(width), str(height)])
    else:
        logger.warning("edmcoverlay2: not starting overlay, already running")


def stop_overlay():
    global overlay_process
    if overlay_process:
        logger.info("edmcoverlay2: stopping overlay")
        overlay_process.terminate()
        overlay_process.communicate()
        overlay_process = None
    else:
        logger.warning("edmcoverlay2: not stopping overlay, not started")


def plugin_start3(plugin_dir):
    logger.info("edmcoverlay2: plugin start!")
    return "edmcoverlay2"


def journal_entry(cmdr, is_beta, system, station, entry, state):
    global overlay_process
    if entry["event"] in ["LoadGame", "StartUp"] and overlay_process is None:
        logger.info("edmcoverlay2: load event received, starting overlay")
        start_overlay()
    elif entry["event"] in ["Shutdown", "ShutDown"]:
        logger.info("edmcoverlay2: shutdown event received, stopping overlay")
        stop_overlay()


def plugin_stop():
    global overlay_process
    logger.info("edmcoverlay2: exiting plugin")
    if environ.get('XDG_SESSION_TYPE', 'X11') == 'X11':
        edmcoverlay.edmcoverlay._the_overlay._stop()
    stop_overlay()


def plugin_prefs(parent: nb.Notebook, cmdr: str, is_beta: bool) -> nb.Frame:
    global xpos_var, ypos_var, width_var, height_var
    xpos_var = tk.IntVar(value=config.get_int("edmcoverlay2_xpos") or 0)
    ypos_var = tk.IntVar(value=config.get_int("edmcoverlay2_ypos") or 0)
    width_var = tk.IntVar(value=config.get_int("edmcoverlay2_width") or 1920)
    height_var = tk.IntVar(value=config.get_int("edmcoverlay2_height") or 1080)
    frame = nb.Frame(parent)
    frame.columnconfigure(0, weight=1)
    PAD_X = 10
    PAD_Y = 2

    f0 = nb.Frame(frame)
    HyperlinkLabel(f0, text="edmcoverlay2", url="https://github.com/sersorrel/edmcoverlay2", background=nb.Label().cget('background'), underline=True).grid(row=0, column=0, sticky=tk.W, padx=(PAD_X, 0))
    nb.Label(f0, text="by Ash Holland").grid(row=0, column=1, sticky=tk.W, padx=(0, PAD_X))
    f0.grid(sticky=tk.EW)

    ttk.Separator(frame, orient=tk.HORIZONTAL).grid(padx=PAD_X, pady=2 * PAD_Y, sticky=tk.EW)

    f1 = nb.Frame(frame)
    nb.Label(f1, text="Overlay configuration:").grid(row=0, column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky=tk.W)
    nb.Label(f1, text="X position").grid(row=1, column=0, padx=PAD_X, pady=(PAD_Y, 0), sticky=tk.E)
    nb.Entry(f1, textvariable=xpos_var).grid(row=1, column=1, columnspan=3, padx=(0, PAD_X), pady=PAD_Y, sticky=tk.W)
    nb.Label(f1, text="Y position").grid(row=2, column=0, padx=PAD_X, pady=(PAD_Y, 0), sticky=tk.E)
    nb.Entry(f1, textvariable=ypos_var).grid(row=2, column=1, columnspan=3, padx=(0, PAD_X), pady=PAD_Y, sticky=tk.W)
    nb.Label(f1, text="Width").grid(row=3, column=0, padx=PAD_X, pady=(PAD_Y, 0), sticky=tk.E)
    nb.Entry(f1, textvariable=width_var).grid(row=3, column=1, columnspan=3, padx=(0, PAD_X), pady=PAD_Y, sticky=tk.W)
    nb.Label(f1, text="Height").grid(row=4, column=0, padx=PAD_X, pady=(PAD_Y, 0), sticky=tk.E)
    nb.Entry(f1, textvariable=height_var).grid(row=4, column=1, columnspan=3, padx=(0, PAD_X), pady=PAD_Y, sticky=tk.W)
    f1.grid(sticky=tk.EW)

    ttk.Separator(frame, orient=tk.HORIZONTAL).grid(padx=PAD_X, pady=2 * PAD_Y, sticky=tk.EW)

    f2 = nb.Frame(frame)
    nb.Label(f2, text="Manual overlay controls:").grid(row=0, column=0, padx=PAD_X, pady=PAD_Y)
    nb.Button(f2, text="Start overlay", command=lambda: start_overlay()).grid(row=0, column=1, padx=PAD_X, pady=PAD_Y)
    nb.Button(f2, text="Stop overlay", command=lambda: stop_overlay()).grid(row=0, column=2, padx=PAD_X, pady=PAD_Y)
    f2.grid(sticky=tk.EW)

    return frame


def prefs_changed(cmdr: str, is_beta: bool) -> None:
    xpos = xpos_var.get()
    ypos = ypos_var.get()
    width = width_var.get()
    height = height_var.get()
    change = False
    for name, val in [("xpos", xpos), ("ypos", ypos), ("width", width), ("height", height)]:
        try:
            assert int(val) >= 0
        except (ValueError, AssertionError):
            logger.warning("Bad config value for %s: %r", name, val)
        else:
            try:
                old_val = config.get_int(f"edmcoverlay2_{name}")
            except (TypeError, ValueError):
                pass
            else:
                if val != old_val:
                    change = True
            config.set(f"edmcoverlay2_{name}", val)
    if change and overlay_process is not None:
        logger.info("Settings changes detected, restarting overlay")
        stop_overlay()
        start_overlay()

        
def debugconsole():
    """
    Print stuff
    """
    start_overlay()

    cl = edmcoverlay.Overlay()

    while True:
        line = sys.stdin.readline().strip()
        cl.send_message("msg", line, "red", 100, 100)

        
if __name__ == "__main__":
    debugconsole()
