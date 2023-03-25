import logging
import socket
from typing import Optional


class Client:
    MAX_SIZE = 8000  # Max message size
    LEN_BYTES = 2  # How many bytes to use for the len of the message
    # Make sure MAX_SIZE is less than 2^(8*LEN_BYTES)

    def __init__(self, socket: socket.socket):
        self.socket = socket
        self.buffer = bytes()

    def _parse_message(self) -> Optional[str]:
        """
        Parses a message from the data bytes.
        If the message is incomplete, returns None
        """
        if len(self.buffer) < self.LEN_BYTES:
            return None

        message_length = int.from_bytes(
            self.buffer[: self.LEN_BYTES], "big", signed=False
        )
        total_len = self.LEN_BYTES + message_length
        if len(self.buffer) < total_len:
            return None
        
        result = self.buffer[self.LEN_BYTES : total_len].decode()
        self.buffer = self.buffer[total_len:]
        return result

    def recv_message(self):
        """
        Receives a message from the client.
        Returns None if socket is closed.
        """
        if not self.socket:
            return None

        result = self._parse_message()
        while not result:
            new_data = self.socket.recv(1024)
            if not new_data:
                if len(self.buffer):
                    logging.error(
                        f"Error: client disconnected but there are {len(self.buffer)} unused bytes"
                    )
                return None
            self.buffer += new_data
            result = self._parse_message()
        return result

    def send_message(self, message: str):
        """
        Sends a message to the client.
        Does nothing if the socket is closed
        """
        if not self.socket:
            return
        encoded = message.encode()
        if len(encoded) > self.MAX_SIZE:
            raise Exception(f"Message exceeds max size ({self.MAX_SIZE})")

        to_send = len(encoded).to_bytes(self.LEN_BYTES, "big", signed=False)
        to_send += encoded
        self.socket.sendall(to_send)

    def close(self):
        if not self.socket:
            return None
        self.socket.close()
        self.socket = None
