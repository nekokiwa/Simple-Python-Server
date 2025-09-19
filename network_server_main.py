
from configfile import *
from configfile import LOG_FILE
from network_utilities import *
from ClientHandler import *
from network_server_controller import server_control

import socket
import _thread
import atexit
import sys


def main():
    """setup and begin running the server"""
    #setup
    client_names:list[ClientName] = []
    connected_clients:list[ClientHolder] = []
    load_names(client_names, NAMES_FILE)
    port:int = PORT_TO_USE
    s:SocketType = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host:str = socket.gethostname()
    log_message(LOG_FILE,f'\n##########################\nstarting new session with:\nip:{host}||port:{port}')
    s.bind((host,port))
    s.listen(100)
    running:bool = True
  
    #called on script exit
    @atexit.register
    def on_exit():
        #log end of session
        log_message(LOG_FILE,f"ending session with:\nip:{host}||port:{port}")

    #start the thread for controlling the server
    _thread.start_new_thread(server_control,(host, port, connected_clients, client_names))

    #running code
    while running:
        try:
            #establish connection
            client, addr = s.accept()
            holder:ClientHolder = ClientHolder(client, addr)
            #handle client
            _thread.start_new_thread(ClientHandler,(holder, connected_clients, client_names))

        except KeyboardInterrupt:
            #close program on interrupt
            sys.exit()
        except Exception as x:
            #log any errors but don't crash if we don't need to
            log_message(LOG_FILE,f"exception: ({x}) happened in main code...")
            pass




if __name__ == "__main__":
  main()
