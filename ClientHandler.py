
import traceback


from configfile import * 
from socket import SocketType
from ClientName import *
from network_utilities import *

class ClientHandler:
  def __init__(self,holder:ClientHolder, connected_clients, client_names) -> None:
    self.holder = holder
    self.has_client = True
    log_message(LOG_FILE,f"connection opened from {holder.addr}")
    self.handle_client(connected_clients, client_names)

  def close_client(self, connected_clients):
    """closes the client connection"""
    addr = self.holder.addr

    self.has_client = False
    connected_clients.remove(self.holder)
    try:
      self.holder.sock.close()
    except OSError:
      log_message(f'os error closing thread handling {addr}. ignoring')
      pass
    log_message(LOG_FILE,f"connection with {addr} closed by thread")

  def send_msg(self, to_send:str):
    send_message(to_send,self.holder.sock,self.holder.addr)

  def handle_command(self,cmd:str, client_names) -> str:
    """handles the given command and returns the message to send"""
    addr = self.holder.addr
    client = self.holder.sock
    message = "Error message" #default message in case command handler did not specify

    match cmd.lower(): #match lower to ignore case
        case "hello":
            message = "Hello, World!"
        case "set name":
            needs_name = True
            while needs_name:
                self.send_msg("please enter the name you want to set for your ip address")
                msg = client.recv(1024).decode('utf-8')
                if not msg:
                    #do nothing if no message sent
                    break
                add_name(addr, msg, client_names)
                needs_name = False
                message = f"name set to: {msg}"
        case "get name":
            message = get_name(addr, client_names)
        case "help":
            message = unset(HELP_MESSAGE_SET)
        case "null":
            message = "\0"
        case "return":
            message = "\n"
        case 'close':
            message = 'close'
        case '\0\0\0\0\0\0\0\0':
            message = 'close'
        case 'download':
            needs_name = True
            while needs_name:
                self.send_msg("please enter the name of the file to download, including the extension")
                msg = client.recv(1024).decode('utf-8')
                if not msg:
                    #do nothing if no message sent
                    break
            
                self.send_msg("begin ft")
                self.send_msg(msg)

                msg = ACCESSIBLE_FILES_FOLDER + msg
                filesize = os.stat(msg).st_size
                self.send_msg(str(filesize))
                if client.recv(1024).decode('utf-8') != 'ready':
                    message = "file transfer cancelled or failed."
                else: 
                    send_file(msg, client, addr)
                    message = "\n\nFile transfer finished!"
                needs_name = False
        case 'cat gay':
            message = "mrow mrow mrrrp nya :3"
        case 'send to':
            needs_target = True
            needs_msg = True

            while needs_target:
                self.send_msg("please enter the name or ip of the client to send a message to")

            while needs_msg:
                self.send_msg("please enter the ")
        case _:
            message = f"Command ({cmd}) received."
    return message

  def handle_client(self, connected_clients, client_names):
    """function for handling a client meant to be used in a thread"""
    #setup
    holder = self.holder
    client = holder.sock
    addr = holder.addr
    connected_clients.append(holder)
    #receive messages
    try:
      self.send_msg(WELCOME_MSG)
      while self.has_client:
        msg = client.recv(1024).decode('utf-8')
        if not msg:
          #do nothing if no message sent
          break
        log_message(LOG_FILE,f"received message from {addr}: {msg}")
        if msg == "close":
          self.send_msg('close')
          self.close_client()
        else:
          # to_send = input("Message for client:\n")
          to_send = self.handle_command(msg, client_names)
          self.send_msg(to_send)
          if to_send == 'close':
            self.close_client()
    except Exception as x:
      #log error without crashing main
      log_message(LOG_FILE,f"\nException ({x}) raised in thread handling client at: {addr}\nTRACE:\n{traceback.format_exc()}\n")
      try:
        client.close()
      except Exception as x2:
        #don't crash main when closing client
        log_message(LOG_FILE, f"Second exception ({x}) when closing: {addr}")
      self.close_client(connected_clients)
    finally:
      log_message(LOG_FILE,f"closed thread handling: {addr}")