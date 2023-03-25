import socket
import logging
import errno
import signal

class Server:
    BUF_SIZE = 1024

    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        signal.signal(signal.SIGTERM, lambda *_: self.stop())

    def stop(self):
        # the .shutdown() also stops the .accept() in __handle_client_connection
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()
        logging.info(f'action: server_socket_closed | result: success')


    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        while True:
            client_sock = self.__accept_new_connection()
            if not client_sock:
                break
            self.__handle_client_connection(client_sock)

    def __handle_client_connection(self, client_sock: socket.socket):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            data = bytes()
            received = client_sock.recv(1024)
            while received:
                data += received
                received = client_sock.recv(1024)
            msg = data.rstrip().decode('utf-8')
            addr = client_sock.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
            client_sock.sendall("{}\n".format(msg).encode('utf-8'))
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()
            logging.info(f'action: client_socket_closed | result: success | ip: {addr[0]}')

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned.

        If the socket is closed, the function returns None.
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        try:
            c, addr = self._server_socket.accept()
        except OSError as e:
            if e.errno in (errno.EINVAL, errno.EBADF):
                # This happens when the socket is invalid, and is raised
                # when the socket is closed from somewhere else. This means
                # the application is shutting down.
                return None
            raise
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
