
from ClientName import ClientName
from configfile import *
from socket import SocketType
import os


def load_names(client_names, filename):
    """loads the names from file into client names list"""
    try:
        with open(filename,'r') as file:
            lines = file.readlines()
            for line in lines: #each name is separated by lineberaks, one name per line
                ip = ""
                name = ""
                getting_ip = True
                for char in line:
                    if getting_ip:
                        if char == ':': #ip separated from name by a colon
                            getting_ip = False
                        else:
                            ip += char
                    else:
                        if char == '\n':
                            break
                    name += char
                if not getting_ip: # check to make sure ip was successfully parsed
                    client_names.append(ClientName(ip,name))
    except FileNotFoundError as fnf:
        #create names.txt if it doesn't exist
        open(filename, "w").close()
        load_names(client_names, filename)

def log_message(log_file:str,message:str):
    """logs a message in the given file and prints to the console"""
    print(message)
    with open(log_file,'a') as file:
        file.write(message + '\n')

def unset(str_set:set[str]) -> str:
    """returns a single string containing the contents of a set of strings"""
    returnstr = ""
    for string in str_set:
        returnstr += string
    return returnstr


def saved_ips(client_names:list) -> list:
    """returns a list of saved ips"""
    ips = []
    for client_name in client_names:
        ips.append(client_name.ip)
    return ips

def add_name(addr, name, client_names):
    """adds a name for the ip in addr"""
    ip = addr[0]
    log_message(LOG_FILE,f"adding name ({name}) for ip: {ip}")

    if ip in saved_ips(client_names):
        #modify existing names
        for client_name in client_names:
            if client_name.ip == ip:
                client_name.name = name
    else:
        #add new names for new ips
        client_names.append(ClientName(ip,name))
    #save name changes to file
    save_names(client_names)

def get_name(addr:tuple, client_names:list[ClientName]) -> str:
    """gets the name of the ip in addr"""
    #check all saved names for ip
    #NOTE changing to a sorted list and faster search algorithm could be a good idea for *large* lists of names
    for client_name in client_names:
        if client_name.ip == addr[0]:
            return client_name.name
    return UNSET_NAME_MSG.format(addr[0])

def has_name(addr:tuple, client_names) -> bool:
    return get_name(addr, client_names) != UNSET_NAME_MSG.format(addr[0])

def save_names(client_names):
    """saves client names to file"""
    with open(NAMES_FILE,'w') as file:
        for name in client_names:
            file.write(f"{name.ip}:{name.name}\n")
    log_message(LOG_FILE,"saved ip names to file")


def send_message(to_send:str,client:SocketType,addr:tuple):
    """sends a message to the client and logs the activity"""
    ORIG = to_send
    
    client.send(to_send.encode('utf-8'))
    log_message(LOG_FILE, f"sent message ({ORIG}) to {addr}")

  
def get_port() -> int:
    """gets an integer from user input to use as port"""
    while True:
        try:
            port = input("enter a port number:\n")
            #TODO add more input checks for out of range ports
            port = int(port)
            return port
        except ValueError:
            print("Invalid port number")
            pass

def send_file(filename:str, client:SocketType, addr:tuple):
    """sends a file to the client"""
    with open(filename, 'rb') as file_to_send:
        #setup
        current_prog = 0
        filesize = os.stat(filename).st_size
        bytes_read = 0

        log_message(LOG_FILE, f"filesize: ({filesize})\nbeginning file transfer...)")
        while bytes_read < filesize:
            to_send = file_to_send.read(FILESENDINGBUFFER)
            bytes_read = file_to_send.tell()
            client.send(to_send)
            prog_percent = (bytes_read / filesize * 100)
            if prog_percent // PPERCENT_INTERVAL > current_prog // PPERCENT_INTERVAL:
                current_prog = (prog_percent // PPERCENT_INTERVAL) * PPERCENT_INTERVAL
                log_message(LOG_FILE, f"transferred {current_prog}%")
        log_message(LOG_FILE, f"file fully transferred")
    send_message('done', client, addr) #finish handshake with client
        
    
def recv_file(server:SocketType, FILESENDINGBUFFER:int):
    """receives a file from the server"""
    print('receiving file')
    filename = server.recv(RECEIVE_BUFFER).decode('utf-8')
    filesize = int(server.recv(RECEIVE_BUFFER).decode('utf-8'))
    server.send('ready'.encode('utf-8'))
    print('sent ready')
    current_prog = 0

    #downloads folder needs to be already created to work
    with open(('downloads/' + filename), 'wb') as file:
        print('file open')
        num = 0
        while num < filesize:
            contents = server.recv(FILESENDINGBUFFER)
            if len(contents) > filesize - num:
                contents = contents[:filesize - num]
            num += file.write(contents)

            prog_percent = (num / filesize * 100)
            if prog_percent // PPERCENT_INTERVAL > current_prog // PPERCENT_INTERVAL:
                current_prog = (prog_percent // PPERCENT_INTERVAL) * PPERCENT_INTERVAL
                print(f"downloaded {current_prog}%...")
        print('\ndone recieving\n')

    print(f'file closed after writing: {num}')