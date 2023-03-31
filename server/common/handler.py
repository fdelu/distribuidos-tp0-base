from multiprocessing import Lock, Queue
import logging
import socket
from typing import Iterable


from .utils import Bet, store_bets
from .client import Client
from .messages import Message, MessageTypes

bets_lock = Lock()

class ClientHandler:
    def __init__(self, client_socket: socket.socket):
        self.client = Client(client_socket)
        self.addr = client_socket.getpeername()

    def get_message(self):
        """
        Receives a single Message from the client.
        Returns None if the socket was closed or an error ocurred.
        """
        try:
            msgData = self.client.recv_message()
            if not msgData:
                return None
            msg = Message.from_string(msgData)
            logging.debug(f'action: receive_message | result: success | ip: {self.addr[0]} | type: {msg.type}')
            return msg
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
            return None
    
    def store_bets(self, bets: list[Bet]):
        """
        Stores the bets in the bet file.
        Thread/Process safe. 
        """
        bets_lock.acquire()
        store_bets(bets)
        bets_lock.release()
        
    def get_bets(self) -> tuple[int, int]:
        """
        Receives all of the bets from the client agency and stores them on a file.
        Returns the number of submitted bets and the agency number of the client
        """
        submitted_bets = 0
        agency = None

        msg = self.get_message()
        while True:
            if not msg:
                logging.warn("action: received_bets | result: warn | no message received, client disconnected")
                break

            if msg.type == MessageTypes.SUBMIT:
                self.store_bets(msg.payload)
                logging.debug(f"action: received_bets | result: success | amount: {len(msg.payload)}")
                self.client.send_message(Message(MessageTypes.SUBMIT_RESULT, "OK").to_string())
                submitted_bets += len(msg.payload)
                agency = msg.payload[0].agency
            elif msg.type == MessageTypes.GET_WINNERS:
                break
            else:
                raise Exception("Not implemented")
            msg = self.get_message()
        return submitted_bets, agency

    def send_winners(self, winners: Iterable[Bet], agency_number: int) -> int:
        """
        Sends all of the winner bets' document number to the agency of this client.

        Receives a list of all of the winners bets (from any agency) and the agency
        number of this clients.

        Returns the amount of winners for this agency.
        """
        this_agency_winners = [x.document for x in winners if x.agency == agency_number]
        msg = Message(MessageTypes.WINNERS, this_agency_winners)
        self.client.send_message(msg.to_string())
        return len(this_agency_winners)

    def close(self):
        """
        Closes and disconnects the internal client
        """
        self.client.close()
        logging.info(f'action: client_disconnected | '
                     f'result: success | ip: {self.addr[0]}')