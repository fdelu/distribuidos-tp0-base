from concurrent.futures import Future, ProcessPoolExecutor, as_completed
from multiprocessing import Manager, Queue, get_context
from multiprocessing.managers import ListProxy
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

        self.handlers: dict[any, ClientHandler] = {}
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

    def __wait_for_futures(futures: list[Future], action: str, *outputs: list[str]) -> list:
        results = []
        for f in as_completed(futures):
            try:
                logging.info(
                    f"action: {action} | result: success | "
                    + " | ".join(f"{x}: {y}" for x,y in zip(outputs, f.result()))
                )
                results.append(f.result())
            except Exception as e:
                logging.info(
                    f"action: {action} | result: error | "
                    f"error: {e}"
                )
        return results

    def get_bets(self):
        futures: list[Future] = []
        max_workers = min(os.cpu_count(), self.num_agencies)

        ctx = get_context("fork")
        with ProcessPoolExecutor(max_workers, mp_context=ctx) as e:
            while len(futures) < self.num_agencies:
                client_sock = self.__accept_new_connection()
                if not client_sock:
                    break

                handler = ClientHandler(client_sock)
                self.handlers[handler.addr] = handler
                futures.append(e.submit(worker_get_bets, handler))
            
            results = Server.__wait_for_futures(futures, "get_bets", "agency", "address", "submitted_bets")
            for agency, address, _ in results:
                self.handlers[address].agency = agency

        logging.info(f"action: sorteo | result: success")
        self._server_socket.close()

    def send_winners(self):
        max_workers = min(os.cpu_count(), self.num_agencies)
        futures: list[Bet] = []
        ctx = get_context("fork")
        winners = [x for x in load_bets() if has_won(x)]
        with ProcessPoolExecutor(max_workers, mp_context=ctx) as e:
            
            for handler in self.handlers.values():
                futures.append(e.submit(worker_send_winners, handler, winners))

            Server.__wait_for_futures(futures, "send_winners", "agency", "agency_winners")

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        self.get_bets()
        self.send_winners()
        for handler in self.handlers.values():
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

def worker_get_bets(client: ClientHandler):
    total_submitted = client.get_bets()
    return client.agency, client.addr, total_submitted

def worker_send_winners(client: ClientHandler, all_winners: list[Bet]):
    this_agency_winners = client.send_winners(all_winners)
    return client.agency, this_agency_winners