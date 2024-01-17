import socket
import json
import logging


SERVER_ADDRESS = "127.0.0.1"
SERVER_PORT = 5010

class Overlay(object):
    """
    Client for EDMCOverlay
    """

    def __init__(self, server=SERVER_ADDRESS, port=SERVER_PORT, args=[]):
        self.server = server
        self.port = port
        self.args = args

    def connect(self):
        """
        open the connection
        :return:
        """
        connection = socket.socket()
        connection.connect((self.server, self.port))
        return connection
    
    def send_raw(self, msg):
        """
        Encode a dict and send it to the server
        :param msg:
        :return:
        """
        try:
            connection = self.connect()
        except ConnectionRefusedError as err:
            logging.error(f'connection to {self.server}:{self.port} refused')
            return

        assert isinstance(msg, dict)

        try:
            data = json.dumps(msg)
            connection.send(data.encode("utf-8"))
            connection.send(b"\n")
            connection.close()
        except Exception as err:
            logging.error(f'send_raw failed with {err}')
            raise
        return None

    def send_message(self, msgid, text, color, x, y, ttl=4, size="normal"):
        """
        Send a message
        :param msgid:
        :param text:
        :param color:
        :param x:
        :param y:
        :param ttl:
        :param size:
        :return:
        """
        msg = {"id": msgid,
               "color": color,
               "text": text,
               "size": size,
               "x": x, "y": y,
               "ttl": ttl}
        self.send_raw(msg)

    def send_shape(self, shapeid, shape, color, fill, x, y, w, h, ttl):
        """
        Send a shape
        :param shapeid:
        :param shape:
        :param color:
        :param fill:
        :param x:
        :param y:
        :param w:
        :param h:
        :param ttl:
        :return:
        """
        msg = {"id": shapeid,
               "shape": shape,
               "color": color,
               "fill": fill,
               "x": x, "y": y,
               "w": w, "h": h,
               "ttl": ttl
               }
        self.send_raw(msg)

