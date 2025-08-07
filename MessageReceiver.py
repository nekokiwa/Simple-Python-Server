from configfile import *
from network_utilities import log_message, recv_file

from socket import SocketType
import _thread

class MessageReceiver:
    """class for handling the receiving of messages from a server for a client"""
    def __init__(self, server:SocketType) -> None:
        """initialise receiver and start receiving messages"""
        self.server = server
        self.receive_messages()

    def close(self):
        """log a close message and interrupt main thread"""
        log_message(CLIENT_LOG_FILE, 'message thread closing')
        _thread.interrupt_main()

    def receive_messages(self):
        """handles messages received from host"""
        try:
            while True:#receive message
                msg = self.server.recv(RECEIVE_BUFFER).decode('utf-8')
                if not msg:
                    pass#do nothing if no message received
                log_message(CLIENT_LOG_FILE, f'received message: {msg}')
                if msg == 'close':
                    self.close()
                    break
                elif msg == 'begin ft':
                    #special case for file transfers
                    recv_file(self.server, FILESENDINGBUFFER)
                
        except Exception as x:
            #log errors and close gracefully
            log_message(CLIENT_LOG_FILE, f"exception in message thread: {x}")
            self.close()