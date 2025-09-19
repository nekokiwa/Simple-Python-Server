from socket import SocketType

class ClientHolder:
    """an object that holds the socket and address of a client connection"""
    def __init__(self,sock:SocketType,addr:tuple) -> None:
        self.sock:SocketType = sock
        self.addr:tuple[str, int] = addr

class ClientName:
    """a name linked to an ip used to more easily store client info"""
    def __init__(self, ip:str, name:str) -> None:
        self.ip:str = ip
        self.name:str = name