import logging
import socket


from .utils import store_bets
from .client import Client
from .messages import Message


class ClientHandler:
    def __init__(self, client_socket: socket.socket):
        self.client = Client(client_socket)
        self.addr = client_socket.getpeername()

    def get_message(self):
        try:
            msgData = self.client.recv_message()
            if not msgData:
                return
            msg = Message.from_json(msgData)
            logging.debug(f'action: receive_message | result: success | ip: {self.addr[0]} | type: {msg.type}')
            return msg
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
            return None

        
    def handle(self):
        msg = self.get_message()
        total_bets = 0
        agency = None
        while msg:
            if msg.type == Message.SUBMIT_TYPE:
                store_bets(msg.payload)
                logging.debug(f"action: received_bets | result: success | cantidad: {len(msg.payload)}")
                self.client.send_message(Message(Message.SUBMIT_RESULT_TYPE, "OK").to_json())
                total_bets += len(msg.payload)
                agency = msg.payload[0].agency
            else:
                raise Exception("Not implemented")
            msg = self.get_message()
        
        self.client.close()
        logging.info(f'action: client_disconnected | submitted: {total_bets} | '
                     f'result: success | ip: {self.addr[0]} | agency: {agency}')