from configfile import *
from network_utilities import log_message, recv_file

from socket import SocketType
import _thread

class MessageReceiver:
    def __init__(self, server:SocketType) -> None:
        self.server = server
        self.receive_messages()

    def receive_messages(self):
        """handles messages received from host"""

        def close():
            log_message(CLIENT_LOG_FILE, 'message thread closing')
            _thread.interrupt_main()


        try:
            while True:#receive message
                msg = self.server.recv(RECEIVE_BUFFER).decode('utf-8')
                if not msg:
                    pass#do nothing if no message received
                log_message(CLIENT_LOG_FILE, f'received message: {msg}')
                if msg == 'close':
                    close()
                    break
                elif msg == 'begin ft':
                    recv_file(self.server, FILESENDINGBUFFER)
                
        except Exception as x:
            log_message(CLIENT_LOG_FILE, f"exception in message thread: {x}")
            close()