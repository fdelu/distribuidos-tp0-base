from multiprocessing import Lock, Queue
import logging
import socket
from typing import Iterable


from .utils import Bet, store_bets
from .client import Client
from .messages import Message

bets_lock = Lock()

class ClientHandler:
    def __init__(self, client_socket: socket.socket):
        self.client = Client(client_socket)
        self.addr = client_socket.getpeername()
        self.agency = None
        self.submitted_bets = 0

    def get_message(self):
        try:
            msgData = self.client.recv_message()
            if not msgData:
                return None
            msg = Message.from_json(msgData)
            logging.debug(f'action: receive_message | result: success | ip: {self.addr[0]} | type: {msg.type}')
            return msg
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
            return None

        
    def get_bets(self) -> int:
        msg = self.get_message()
        while True:
            if not msg:
                logging.warn("action: received_bets | result: warn | no message received, client disconnected")
                break

            if msg.type == Message.SUBMIT_TYPE:
                bets_lock.acquire()
                store_bets(msg.payload)
                bets_lock.release()
                logging.debug(f"action: received_bets | result: success | cantidad: {len(msg.payload)}")
                self.client.send_message(Message(Message.SUBMIT_RESULT_TYPE, "OK").to_json())
                self.submitted_bets += len(msg.payload)
                self.agency = msg.payload[0].agency
            elif msg.type == Message.GET_WINNERS_TYPE:
                break
            else:
                raise Exception("Not implemented")
            msg = self.get_message()
        return self.submitted_bets

    def send_winners(self, winners: Iterable[Bet]) -> int:
        this_agency_winners = [x.document for x in winners if x.agency == self.agency]
        msg = Message(Message.WINNERS_TYPE, this_agency_winners)
        self.client.send_message(msg.to_json())
        return len(this_agency_winners)

    def close(self):
        self.client.close()
        logging.info(f'action: client_disconnected | '
                     f'result: success | ip: {self.addr[0]}')