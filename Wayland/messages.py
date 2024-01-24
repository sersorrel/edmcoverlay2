import threading
import logging

class Messages(object):
    class RepeatTimer(threading.Timer):
        def run(self):
            while not self.finished.wait(self.interval):
                self.function(*self.args, **self.kwargs)

    def __init__(self):
        self._msg_lock = threading.RLock()
        self._msgs = {}
        self._timer = self.RepeatTimer(1, self.tick_ttls)
        self._timer.start()

    def stop_timer(self):
        self._timer.cancel()

    def add_message(self, msg):
        with self._msg_lock:
            self._msgs[msg['id']] = msg

    def add_messages(self, msgs: list):
        with self._msg_lock:
            for msg in msgs:
                self._msgs[msg['id']] = msg

    def get_messages(self):
        with self._msg_lock:
            for _, message in self._msgs.items():
                yield message

    def tick_ttls(self):
        logging.debug(f'ttl tick')
        with self._msg_lock:
            for message_id in list(self._msgs.keys()):
                self._msgs[message_id]['ttl'] -= 1
                if self._msgs[message_id]['ttl'] <= 0:
                    self._msgs.pop(message_id)
