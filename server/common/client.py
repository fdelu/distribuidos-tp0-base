import socket
from typing import Optional


class Client:
    LEN_BYTES = 2

    def __init__(self, socket: socket.socket):
        self.socket = socket
    
    def _parse_message(data: bytes) -> Optional[str]:
        """
        Parses a message from the data bytes.
        If the message is incomplete, returns None
        """
        if len(data) < Client.LEN_BYTES:
            return None
        message_length = int.from_bytes(data[:Client.LEN_BYTES], 'big', signed=False)

        if len(data) < Client.LEN_BYTES + message_length:
            return None
        
        return data[Client.LEN_BYTES:].decode()

    def recv_message(self):
        """
        Receives a message from the client.
        Returns None if socket is closed.
        """
        if not self.socket:
            return None
        
        received = self.socket.recv(1024)
        result = Client._parse_message(received)
        while not result:
            received += self.socket.recv(1024)
            result = Client._parse_message(received)
        return result
    
    def close(self):
        if not self.socket:
            return None
        self.socket.close()
        self.socket = None