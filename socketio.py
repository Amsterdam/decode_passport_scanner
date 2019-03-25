from socketIO_client import SocketIO
from session import SessionStatus

from threading import Thread
import time, logging

class SocketCom:
    """
    TODO:
    - add doc
    """
    def __init__(self, ready, api_url):
        self.ready = ready
        self.session_status = None

        self.socket_thread = SocketThread(self, api_url)
        self.socket_thread.daemon = True
        self.socket_thread.start()
        
    def join_room(self, room):
        self.socket_thread.join_room(room)

    def on_status_update(self, data):
        self.session_status = data['status']
        logging.info("Session status update [{}]".format(self.session_status))
        
        if self.session_status == SessionStatus.GOT_PUB_KEY.value:
            self.ready.set()


class SocketThread(Thread):
    """
    TODO:
    - add doc
    """
    def __init__(self, parent, api_url):
        Thread.__init__(self)
        self.parent = parent
        self.socketIO = SocketIO(api_url)
        self.socketIO.on('status_update', self.parent.on_status_update)

    def join_room(self, room):
        self.socketIO.emit('join_room', {'session_id': room})

    def run(self):
        self.socketIO.wait()