from socket import SocketType

class ClientHolder:
    def __init__(self,sock:SocketType,addr:tuple) -> None:
        self.sock = sock
        self.addr = addr

class ClientName:
    def __init__(self, ip:str, name:str) -> None:
        self.ip = ip
        self.name = name