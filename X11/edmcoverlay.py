import logging
import secrets
from pathlib import Path

from config import appname

plugin_name = Path(__file__).parent.parent.name
logger = logging.getLogger(f"{appname}.{plugin_name}")

logger.debug("edmcoverlay2: lib loaded")

import errno
import json
import re
import socket
import threading
import time
from functools import wraps

IS_PRETENDING_TO_BE_EDMCOVERLAY = True

_stopping = False


class _Overlay:
    _instance = None
    _lock = threading.Lock()
    _initialised = False

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = object.__new__(cls, *args, **kwargs)
            return cls._instance

    def __init__(self, server="127.0.0.1", port=5020):
        logger.info("edmcoverlay2: hiiiiiii")
        with self._lock:
            if self._initialised:
                logger.debug("edmcoverlay2: skipping init")
                return
            logger.debug("edmcoverlay2: init")
            self._initialised = True
            self._host = server
            self._port = port
            self._conn = None
            self._overlays = {}
            self._updater = threading.Thread(target=self.__updater)
            self._server = threading.Thread(target=self.__server)
            self._server.start()

    def __updater(self):
        timestep = 1
        global _stopping
        logger.info("edmcoverlay2: updater running")
        had_overlays = False
        while not _stopping:
            time.sleep(timestep)
            if not self._overlays:
                if had_overlays:
                    # print("edmcoverlay2: overlays newly don't exist, sending empty overlay list")
                    had_overlays = False
                else:
                    # print("edmcoverlay2: overlays don't exist and haven't for a while, not sending anything")
                    continue
            else:
                # print(f"edmcoverlay2: overlays exist ({len(self._overlays)} of them), sending them")
                # print("edmcoverlay2: the overlays are:", self._overlays)
                had_overlays = True
            for id in list(self._overlays):
                self._overlays[id]["ttl"] -= timestep
                if self._overlays[id]["ttl"] <= 0:
                    del self._overlays[id]
            content = json.dumps([
                {k: overlay[k] for k in [
                    "x", "y", "color", "text", "size", "shape", "fill", "w", "h", "vector"
                ] if overlay.get(k) is not None}
                for id, overlay in self._overlays.items()
            ]).encode()
            try:
                conn = socket.socket()
                conn.connect((self._host, self._port))
                conn.send(str(len(content)).encode() + b"#" + content)
                conn.close()
            except socket.error as e:
                if e.errno == errno.ECONNREFUSED:
                    logger.warning("edmcoverlay2: conn refused")
                else:
                    raise
        logger.info("edmcoverlay2: updater stopping")

    def __server(self):
        # Pretend to be the EDMCOverlay server.
        global _stopping
        logger.info("edmcoverlay2: server running")
        self._sock = socket.socket()
        self._sock.bind(("127.0.0.1", 5010))
        self._sock.listen()
        self._sock.settimeout(2)
        while not _stopping:
            try:
                sock, _ = self._sock.accept()
            except socket.timeout:
                continue
            logger.debug("edmcoverlay2: server got connection")
            data = b""
            while True:
                chunk = sock.recv(1024)
                if not chunk:
                    break
                data += chunk
                objects = data.split(b"\n")
                for obj in objects[:-1]:
                    msg = json.loads(obj)
                    self.send_raw(msg)
                data = objects[-1]
            sock.close()
            if data:
                msg = json.loads(data)
                # TODO
                self.send_raw(msg)
        logger.info("edmcoverlay2: server stopping")

    def _stop(self):
        global _stopping
        logger.info("edmcoverlay2: stopping client threads")
        _stopping = True
        if self._server is not None and self._server.is_alive():
            logger.info("edmcoverlay2: waiting for server to stop")
            self._server.join()
        if self._updater is not None and self._updater.is_alive():
            logger.info("edmcoverlay2: waiting for updater to stop")
            self._updater.join()
        logger.info("edmcoverlay2: all client threads stopped")

    def send_raw(self, msg):
        # TODO
        logger.debug("edmcoverlay2: send_raw %s", repr(msg))
        self._overlays[msg.get("msgid") or msg.get("shapeid") or msg["id"]] = msg
        if msg["ttl"] <= 0:
            del self._overlays[msg.get("msgid") or msg.get("shapeid") or msg["id"]]
        if not self._updater.is_alive():
            self._updater.start()

    def send_message(self, msgid, text, color, x, y, ttl=4, size="normal"):
        logger.debug("edmcoverlay2: send_message %s", repr([msgid, text, color, x, y, ttl, size]))
        if not text or not color:
            self._overlays.pop(msgid, None)
        else:
            assert color in ["red", "yellow", "blue", "green", "black"] or re.match("#[0-9a-fA-F]{6}", color)
            assert ttl > 0
            assert size in ["normal", "large"]
            self._overlays[msgid] = {
                "text": text,
                "color": color,
                "x": x,
                "y": y,
                "ttl": ttl,
                "size": size,
            }
        if not self._updater.is_alive():
            self._updater.start()

    def send_shape(self, shapeid, shape, color, fill, x, y, w, h, ttl):
        logger.debug("edmcoverlay2: send_shape %s", repr([shapeid, shape, color, fill, x, y, w, h, ttl]))
        if not shape or not color:
            self._overlays.pop(shapeid, None)
        else:
            assert shape in ["rect", "vect"]
            assert color in ["red", "yellow", "blue", "green", "black"] or re.match("#[0-9a-fA-F]{6}", color)
            assert fill in ["red", "yellow", "blue", "green", "black"] or re.match("#[0-9a-fA-F]{6}", fill)
            assert ttl > 0
            self._overlays[msgid] = {
                "shape": shape,
                "color": color,
                "fill": fill,
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "ttl": ttl,
            }
        if not self._updater.is_alive():
            self._updater.start()


class Overlay:
    def __init__(self) -> None:
        self._token = secrets.token_hex(4)
        self._overlay = _Overlay()

    def send_raw(self, msg):
        if "msgid" in msg:
            msg["msgid"] = self._token + str(msg["msgid"])
        if "shapeid" in msg:
            msg["shapeid"] = self._token + str(msg["shapeid"])
        if "id" in msg:
            msg["id"] = self._token + msg["id"]
        return self._overlay.send_raw(msg)

    def send_message(self, msgid, text, color, x, y, ttl=4, size="normal"):
        return self._overlay.send_message(self._token + str(msgid), text, color, x, y, ttl=ttl, size=size)

    def send_shape(self, shapeid, shape, color, fill, x, y, w, h, ttl):
        return self._overlay.send_shape(self._token + str(shapeid), shape, color, fill, x, y, w, h, ttl)


logger.debug("edmcoverlay2: instantiating overlay class")
_the_overlay = _Overlay()
logger.debug("edmcoverlay2: overlay class instantiated")
