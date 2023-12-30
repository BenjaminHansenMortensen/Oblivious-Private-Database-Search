""" Handling the communication with the client """

from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, timeout
from ssl import SSLContext, PROTOCOL_TLS_CLIENT, PROTOCOL_TLS_SERVER
from pathlib import Path


class Communicate:
    """
        Establishes a secure communication channel between the server and client.
        Allowing them to send and receive json files.
    """
    def __init__(self):
        self.HEADER = 1024
        self.LISTEN_PORT = 5500
        self.HOST = 'localhost'
        self.ADDR = (self.HOST, self.LISTEN_PORT)
        self.SERVER_ADDR = ('localhost', 5005)
        self.FORMAT = 'utf-8'

        self.FILE_NAME_MESSAGE = '<FILE NAME>'
        self.FILE_CONTENTS_MESSAGE = '<FILE CONTENTS>'
        self.DISCONNECT_MESSAGE = '<DISCONNECT>'
        self.END_FILE_MESSAGE = '<END FILE>'

        self.server_context = SSLContext(PROTOCOL_TLS_SERVER)
        self.server_context.load_cert_chain(certfile='Client/Networking/Keys/cert.pem', keyfile='Client/Networking/Keys/key.pem', password='password')
        self.client_context = SSLContext(PROTOCOL_TLS_CLIENT)
        self.client_context.load_verify_locations('Server/Networking/Keys/cert.pem')
        self.listen_host = self.server_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_side=True)
        self.listen_host.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.listen_host.settimeout(0.2)

        self.close = False
        self.listen_thread = []
        self.run_thread = Thread(target=self.run)
        self.run_thread.start()

    def add_padding(self, message):
        """
            Encodes and adds the appropriate padding to a message to match the header size.

            Parameters:
                - message (str) : The message to be padded.

            Returns:
                message (bytes) : The padded message.
        """

        message = message.encode(self.FORMAT)
        message += b' ' * (self.HEADER - len(message))
        return message

    def receive_json(self, connection, address):
        """
            Receives the json file and writes it.

            Parameters:
                - connection (socket) : The connection to the sender.
                - address (tuple(str, int)) : The address to receive from.

            Returns:

        """

        while True:
            message = connection.recv(self.HEADER).decode(self.FORMAT).strip()
            if message == self.DISCONNECT_MESSAGE:
                print(f'[DISCONNECTED] {address}')
                return
            elif message == self.FILE_NAME_MESSAGE:
                print(f'[RECEIVED] {message} from {address}')
                file_name = connection.recv(self.HEADER).decode(self.FORMAT).strip()
            elif message == self.FILE_CONTENTS_MESSAGE:
                print(f'[RECEIVING] {message} from {address}')

                file_contents = ''
                while (message := connection.recv(self.HEADER).decode(self.FORMAT).strip()) != self.END_FILE_MESSAGE:
                    file_contents += message

                print(f'[RECEIVED] {message} from {address}')
                with open(f'{file_name}.json', 'w') as file:
                    file.write(file_contents)

    def send_json(self, file_name, file_contents):
        """
            Sends a json file to an address.

            Parameters:
                - json_file (str) : The dictionary to be sent.
                - address (tuple(str, int)) : The address to send to.

            Returns:

        """

        send_host = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')

        send_host.connect(self.SERVER_ADDR)
        send_host.send(self.add_padding(self.FILE_NAME_MESSAGE))
        send_host.send(self.add_padding(f'{file_name}'))
        send_host.send(self.add_padding(self.FILE_CONTENTS_MESSAGE))
        send_host.send(self.add_padding(f'{file_contents}'))
        send_host.send(self.add_padding(self.END_FILE_MESSAGE))
        send_host.send(self.add_padding(self.DISCONNECT_MESSAGE))
        send_host.close()

    def get_file_contents(self, file_path):
        with open(file_path, 'r') as f:
            contents = f.read()

        return contents

    def run(self):
        """
            Starts the listening and handles incoming connections.

            Parameters:
                -

            Returns:

        """

        self.listen_host.bind(self.ADDR)
        self.listen_host.listen()
        print(f'[LISTENING] on (\'{self.HOST}\', {self.LISTEN_PORT})')
        while True:
            if self.close:
                return

            try:
                conn, addr = self.listen_host.accept()
                thread = Thread(target=self.receive_json, args=(conn, addr))
                thread.start()
                self.listen_thread.append(thread)
            except timeout:
                continue
            except Exception:
                print('[ERROR] incoming connection failed')

    def kill(self):
        """
            Closes the communication.

            Parameters:
                -

            Returns:

        """

        for thread in self.listen_thread:
            thread.join()
        self.listen_host.close()
        self.close = True
        self.run_thread.join()
        print(f'[CLOSED] {self.ADDR}')
