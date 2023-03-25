import socket
import logging
import errno
import signal
import os

from .handler import ClientHandler
from .client import Client
from .utils import Bet, has_won, load_bets, store_bets


class Server:
    BUF_SIZE = 1024

    def __init__(self, port, listen_backlog, num_agencies: int):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(("", port))
        self._server_socket.listen(listen_backlog)
        self._agencies: dict[int, ClientHandler] = {}
        self.num_agencies = num_agencies
        signal.signal(signal.SIGTERM, lambda *_: self.stop())

    def stop(self):
        # the .shutdown() also stops the .accept() in __handle_client_connection
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()
        for handler in self._agencies.values():
            handler.close()
        logging.info(f"action: server_socket_closed | result: success")
        os._exit(0)

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        expected_agencies = set(range(1, self.num_agencies + 1))

        while True:
            client_sock = self.__accept_new_connection()
            if not client_sock:
                break
            handler = ClientHandler(client_sock)
            handler.get_bets()
            self._agencies[handler.agency] = handler

            remaining_agencies = expected_agencies.difference(set(self._agencies))
            logging.info(
                "action: process_agency | result: success | "
                f"agency: {handler.agency} | remaining: {remaining_agencies}"
            )
            if len(remaining_agencies) == 0:
                break

        logging.info(f"action: sorteo | result: success")
        self._server_socket.close()
        logging.info(f"action: server_socket_closed | result: success")
        self.__send_winners()

    def __send_winners(self):
        winners = [bet for bet in load_bets() if has_won(bet)]
        for agency in list(self._agencies):
            handler = self._agencies.pop(agency)
            handler.send_winners(winners)
            handler.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned.

        If the socket is closed, the function returns None.
        """

        # Connection arrived
        logging.info("action: accept_connections | result: in_progress")
        try:
            c, addr = self._server_socket.accept()
        except OSError as e:
            if e.errno in (errno.EINVAL, errno.EBADF):
                # This happens when the socket is invalid, and is raised
                # when the socket is closed from somewhere else. This means
                # the application is shutting down.
                return None
            raise
        logging.info(f"action: accept_connections | result: success | ip: {addr[0]}")
        return c
