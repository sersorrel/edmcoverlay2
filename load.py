"""Totally definitely EDMCOverlay."""

import logging
from pathlib import Path
from subprocess import Popen

from config import appname
import plug


plugin_name = Path(__file__).parent.name
logger = logging.getLogger(f"{appname}.{plugin_name}")


logger.debug("edmcoverlay2: loading plugin, importing lib")
import edmcoverlay
logger.debug("edmcoverlay2: got lib: %s", repr(edmcoverlay))
import edmcoverlay._edmcoverlay
logger.debug("edmcoverlay2: got internal lib: %s", repr(edmcoverlay._edmcoverlay))

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
        logger.info("edmcoverlay2: starting overlay")
        overlay_process = Popen([find_overlay_binary()])
    elif entry["event"] in ["Shutdown", "ShutDown"]:
        logger.info("edmcoverlay2: shutdown event received, stopping overlay")
        stop_overlay()


def plugin_stop():
    global overlay_process
    logger.info("edmcoverlay2: exiting plugin")
    edmcoverlay._edmcoverlay._the_overlay._stop()
    stop_overlay()
