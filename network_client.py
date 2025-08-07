

from configfile import *
from network_utilities import *
from MessageReceiver import *
import _thread

from _thread import start_new_thread as new_thread
import time
import socket




def main():
    """setup client process and connect to a server defined by user input"""
  
    #get ip and port
    host_ip = input("enter the ip to connect to:\n")
    port = get_port()
    log_message(CLIENT_LOG_FILE, f"----------------------\np:{port}||ip:{host_ip}")

    #setup socket
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((host_ip,port))

    to_close = False

    #start message handling thread
    new_thread(MessageReceiver, (s, ) )
    
    #message loop
    while not to_close:  
        #get user input
        try:
            to_send = input("enter a message to send to host:\n").encode('utf-8')

            #send message
            log_message(CLIENT_LOG_FILE, f'sending "{to_send}" to server')
            s.send(to_send)
            if to_send == 'close'.encode('utf-8'):
                #break message loop on close message
                to_close = True
                break
            time.sleep(1) # wait one second to allow reply to be sent by server
      
        except KeyboardInterrupt as ki:
            log_message(CLIENT_LOG_FILE, f"Process interrupted. this may have been done by the receiver thread or user themself. Exception: {ki}")
            to_close = True
            s.send('close'.encode('utf-8'))
            break
    log_message(CLIENT_LOG_FILE, 'client process closed')

if __name__ == '__main__':
  main()