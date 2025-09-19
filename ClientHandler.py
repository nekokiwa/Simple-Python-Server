
import traceback


from configfile import * 
from socket import SocketType
from ClientName import *
from network_utilities import *

class ClientHandler:
    """object that handles a client connection including sending and receieving messages"""

    def __init__(self, holder:ClientHolder, connected_clients:list[ClientHolder], client_names:list[ClientName]) -> None:
        """initialise client handler with server and client info and start handling the client"""

        self.holder:ClientHolder = holder
        self.has_client:bool = True
        #automatically start handling client
        log_message(LOG_FILE,f"connection opened from {holder.addr}")
        self.handle_client(connected_clients, client_names)

    def close_client(self, connected_clients:list[ClientHolder]):
        """closes the client connection"""
        addr:tuple[str, int] = self.holder.addr

        self.has_client = False
        connected_clients.remove(self.holder)
        try:
            self.holder.sock.close()
        except OSError:
            log_message(LOG_FILE, f'os error closing thread handling {addr}. ignoring')
        log_message(LOG_FILE, f"connection with {addr} closed by thread")

    def send_msg(self, to_send:str):
        """wrapper function to send a message to the client being handled"""
        send_message(to_send,self.holder.sock,self.holder.addr)
    
    def recv_msg(self, prompt:str|None=None):
        """wrapper function to receive a message from the client being handled"""
        client:SocketType = self.holder.sock
        if prompt:
            self.send_msg(prompt)
        msg:str = client.recv(RECEIVE_BUFFER).decode('utf-8')
        log_message(LOG_FILE, f"received: ({msg}) from {self.holder.addr}")
        return msg

    def handle_command(self, cmd:str, client_names:list[ClientName], connected_clients:list[ClientHolder]) -> str:
        """handles the given command and returns the message to send"""
        addr:tuple[str, int] = self.holder.addr
        message:str = "Error message" #default message in case command handler did not specify

        match cmd.lower(): #match lower to ignore case
            case "hello":
                message = "Hello, World!"
            case "set name":
                needs_name = True
                while needs_name:
                    self.send_msg("please enter the name you want to set for your ip address")
                    msg = self.recv_msg()
                    add_name(addr, msg, client_names)
                    needs_name = False
                    message = f"name set to: {msg}"
            case "get name":
                message = get_name(addr, client_names)
            case "help":
                message = unset(HELP_MESSAGE_SET)
            case "null":
                #for testing purposes
                message = "\0"
            case "return":
                #for testing purposes
                message = "\n"
            case 'close':
                message = 'close'
            case '\0\0\0\0\0\0\0\0':
                #turing complete game network tests needed this for some reason
                message = 'close'
            case 'download':
                message = self.handle_command_download()
            case 'cat gay':
                # :3
                message = "mrow mrow mrrrp nya :3"
            case 'send to':
                message = self.handle_send_to(connected_clients, client_names)
            case _:
                #default message for unknown commands
                message = f"Command ({cmd}) received."
        return message
    
    def handle_send_to(self, connected_clients:list[ClientHolder], client_names:list[ClientName]) -> str:
        """handles sending a message to another client, returns a confirmation or cancellation message"""
        needs_target:bool = True
        target:ClientHolder

        while needs_target:
            name = self.recv_msg("enter the name or ip of the client you wish to send to")
            if name == 'cancel':
                return "message sending canceled"
            for clientname in client_names:
                if name == clientname.name:
                    name = clientname.ip
                    break
            for client in connected_clients:
                if name == client.addr[0]:
                    target = client
                    needs_target = False
                    break
            
        to_send:str = self.recv_msg("enter the message you wish to send")
        send_message(to_send, target.sock, target.addr) # type: ignore
        return "message sent"

    def handle_command_download(self) -> str:
        """helper method for the handle command method, to help handle downloads. returns the message to return"""
        message:str = 'download error' #default download message
        addr:tuple[str, int] = self.holder.addr
        client:SocketType = self.holder.sock

        needs_name:bool = True
        while needs_name:
            filename:str = self.recv_msg(
                "please enter the name of the file to download, including the extension, or 'CANCEL' to cancel")

            if filename == "CANCEL":
                #cancel getting name
                message = "download cancelled"
                needs_name = False
                break
        
            #initiate transfer handshake 
            self.send_msg("begin ft")
            self.send_msg(filename)

            #get and send filesize to client
            path:str = ACCESSIBLE_FILES_FOLDER + filename
            try:
                filesize:int = os.stat(path).st_size
                self.send_msg(str(filesize))

                #only initiate transfer if handshake completes properly
                if self.recv_msg() != 'ready':
                    message = "File transfer cancelled or failed."
                else: 
                    send_file(path, client, addr)
                    message = "\n\nFile transfer finished!"
                needs_name = False
            except FileNotFoundError as fnf:
                self.send_msg("File transfer failed: File does not exist")
        return message

    def handle_client(self, connected_clients:list[ClientHolder], client_names:list[ClientName]):
        """function for handling a client meant to be used in a thread"""
        #setup
        holder:ClientHolder = self.holder
        client:SocketType = holder.sock
        addr:tuple[str, int] = holder.addr
        connected_clients.append(holder)

        #receive messages
        try:
            #send message to client to show successful connection
            self.send_msg(WELCOME_MSG)

            #loop for as long as client is connected
            while self.has_client:
                #check for messages
                msg:str = self.recv_msg()
                if not msg:
                    #do nothing if no message sent
                    break

                #handle receieved messages
                if msg == "close":
                    #special case for closing connection
                    self.send_msg('close')
                    self.close_client(connected_clients)
                else:
                    to_send = self.handle_command(msg, client_names, connected_clients)
                    self.send_msg(to_send)
                    if to_send == 'close':
                        self.close_client(connected_clients)

        except Exception as x:
            #log error without crashing main
            log_message(LOG_FILE, f"\nException ({x}) raised in thread handling client at: {addr}\nTRACE:\n{traceback.format_exc()}\n")
            try:
                client.close()
            except Exception as x2:
                #don't crash main when closing client
                log_message(LOG_FILE, f"Second exception ({x}) when closing: {addr}")

            self.close_client(connected_clients)

        finally:
            log_message(LOG_FILE, f"closed thread handling: {addr}")