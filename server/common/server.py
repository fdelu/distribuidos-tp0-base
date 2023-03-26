from concurrent.futures import Future, ProcessPoolExecutor, as_completed
import socket
import logging
import errno
import signal
import os
from typing import Iterable

from .handler import ClientHandler
from .client import Client
from .utils import Bet, has_won, load_bets, store_bets

Addr = tuple[str, int]

class Server:
    BUF_SIZE = 1024

    def __init__(self, port: int, listen_backlog: int, num_agencies: int):
        """
        Initializes the server socket listener.
        """
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(("", port))
        self._server_socket.listen(listen_backlog)

        self.handlers: dict[int, ClientHandler] = {} # Agency number -> ClienHandler
        self.num_agencies = num_agencies
        signal.signal(signal.SIGTERM, lambda *_: self.__stop())

    def __stop(self):
        """
        Stops the server and closes all of its file descriptors, and exits the program.
        """
        # the .shutdown() also stops the .accept() in __handle_client_connection
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()
        for handler in self._agencies.values():
            handler.close()
        logging.info(f"action: server_socket_closed | result: success")
        os._exit(0)

    def __wait_for_futures(futures: Iterable[Future], action: str, *outputs: list[str]) -> list:
        """
        Waits for all  of the futures to be complete. Logs all of the results (or errors)
        with the provided action name. Prints each future result with the corresponding
        output name.

        Returns a list with the result of successful futures.
        """
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

    def __get_bets(self):
        """
        Connects to the client agencies, and stores all of their bets.

        Populates the self.handlers dictionary.
        """
        futures: list[Future] = []
        handlers_by_addr: dict[Addr, ClientHandler] = {}
        max_workers = min(os.cpu_count(), self.num_agencies)

        with ProcessPoolExecutor(max_workers) as e:
            while len(futures) < self.num_agencies:
                client_sock = self.__accept_new_connection()
                if not client_sock:
                    break

                handler = ClientHandler(client_sock)
                futures.append(e.submit(worker_get_bets, handler))
                handlers_by_addr[handler.addr] = handler
            
            results = Server.__wait_for_futures(futures, "get_bets", "agency", "address", "submitted_bets")
            for agency_num, addr, _ in results:
                self.handlers[agency_num] = handlers_by_addr[addr]

        logging.info(f"action: sorteo | result: success")
        self._server_socket.close()

    def __send_winners(self):
        """
        Gets the winner bets and sends them to the agencies.
        """
        futures: list[Bet] = []
        max_workers = min(os.cpu_count(), self.num_agencies)

        winners = [x for x in load_bets() if has_won(x)]
        with ProcessPoolExecutor(max_workers) as e:
            
            for agency_num, handler in self.handlers.items():
                futures.append(e.submit(worker_send_winners, handler, winners, agency_num))

            Server.__wait_for_futures(futures, "send_winners", "agency", "address", "agency_winners")

    def run(self):
        """
        Runs the server. Gets the bets from all of the channels,
        sends the winners and exits.
        """
        self.__get_bets()
        self.__send_winners()
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

def worker_get_bets(client: ClientHandler) -> tuple[int, Addr, int]:
    """
    Worker function for processes.
    Runs ClientHandler.get_bets()

    Returns the agency number of the client, its address 
    and the amount of bets that were submitted
    """
    total_submitted, agency_num = client.get_bets()
    return agency_num, client.addr, total_submitted

def worker_send_winners(client: ClientHandler, all_winners: list[Bet], agency_num: int) -> tuple[int, Addr, int]:
    """
    Worker function for processes.
    Runs ClientHandler.send_winners()

    Returns the agency number of the client, its address
    and the amount of winners in this agency.
    """
    this_agency_winners = client.send_winners(all_winners, agency_num)
    return agency_num, client.addr, this_agency_winners