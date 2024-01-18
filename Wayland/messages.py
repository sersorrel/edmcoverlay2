import threading
import logging

class Messages(object):
    class RepeatTimer(threading.Timer):
        def run(self):
            while not self.finished.wait(self.interval):
                self.function(*self.args, **self.kwargs)

    def __init__(self):
        self._msg_lock = threading.RLock()
        self._msgs = []
        self._timer = self.RepeatTimer(1, self.tick_ttls)
        self._timer.start()

    def stop_timer(self):
        self._timer.cancel()

    def add_message(self, msg):
        with self._msg_lock:
            self._msgs.append(msg)

    def get_messages(self):
        with self._msg_lock:
            for message in self._msgs:
                yield message

    def tick_ttls(self):
        with self._msg_lock:
            for message in self._msgs:
                logging.info(message)
