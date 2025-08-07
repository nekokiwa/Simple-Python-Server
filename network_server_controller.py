

from network_utilities import *
from configfile import *
from ClientHandler import *

import _thread
import socket






def server_control(host, port, connected_clients, client_names):
    while True:
        cmd = input("enter a command for the server:\n")
        log_message(LOG_FILE,f"server command: ({cmd}) received")

        match cmd.lower():
            case 'quit':
                print('Closing server...')
                _thread.interrupt_main() # raise interrupt in main
                #connect to host socket to stop the accept function waiting
                socket.socket(socket.AF_INET,socket.SOCK_STREAM).connect((host,port))
                break
            case 'log':
                msg = input("please enter the message you wish to log:\n")
                log_message(LOG_FILE,f'CUSTOM LOG: {msg}')
            case 'help':
                #print help message
                print(unset(SERVER_HELP_MESSAGE))
            case 'clients':
                i = 0
                print('clients list:')
                for cli in connected_clients:
                    addr = cli.addr
                    print(f"{i}:({get_name(addr, client_names)}:{addr})")
                    i+=1
            case 'names':
                print("saved names:")
                for name in client_names:
                    print(f"{name.ip}:{name.name}")
            case 'send':
                try:
                    i = int(input("enter the index of the client you wish to send to\n"))
                    try:
                        cli:ClientHolder = connected_clients[i]
                        msg = input("enter the message you wish to send:\n")
                        send_message(msg,cli.sock,cli.addr)
                    except IndexError:
                        print("invalid index. use clients command to get list of clients with indexes")
                    except ConnectionAbortedError:
                        print("Connection to that client was aborted by the client.")
                except ValueError:
                    print("invalid index. index must be integer")
            

            case _:
                print(f"Unknown command: {cmd}")