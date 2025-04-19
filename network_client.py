

from configfile import *
from network_utilities import *
import _thread

from _thread import start_new_thread as new_thread
import time
import socket




def main():
  def message_reciever():
    """handles messages received from host"""

    def close():
      nonlocal to_close
      to_close = True
      _thread.interrupt_main()


    nonlocal s
    nonlocal to_close
    try:
      while True:#receive message
        msg = s.recv(1024).decode('utf-8')
        if not msg:
          pass#do nothing if no message received
        print(f'received message: {msg}')
        if msg == 'close':
          close()
          break
        elif msg == 'begin ft':
            recv_file(s, FILESENDINGBUFFER)
            
    except Exception as x:
      print(f"exception in message thread: {x}")
      close()
  
  #get ip and port
  host_ip = input("enter the ip to connect to:\n")
  port = get_port()
  print(f"p:{port}||ip:{host_ip}")

  #setup socket
  s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.connect((host_ip,port))

  to_close = False

  #start message handling thread
  new_thread(message_reciever,())
  
  #message loop
  while not to_close:  
    #get user input
    try:
      to_send = input("enter a message to send to host:\n").encode('utf-8')

      #send message
      s.send(to_send)
      if to_send == 'close'.encode('utf-8'):
        #break message loop on close message
        to_close = True
        break
      time.sleep(1) # wait one second to allow reply to be sent by server
      
    except KeyboardInterrupt as ki:
      print(f"Process interrupted. this may have been done by the receiver thread or user themself. Exception: {ki}")
      break

if __name__ == '__main__':
  main()