""" Handling the communication with the client """

from time import sleep
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, timeout
from ssl import SSLContext, PROTOCOL_TLS_CLIENT, PROTOCOL_TLS_SERVER

from Oblivious_Database_Query_Scheme.getters import get_server_networking_key_path as server_networking_key_path
from Oblivious_Database_Query_Scheme.getters import get_server_networking_certificate_path as server_networking_certificate_path
from Oblivious_Database_Query_Scheme.getters import get_client_networking_certificate_path as client_networking_certificate_path
from Oblivious_Database_Query_Scheme.getters import get_compare_and_encrypt_mpc_script_path as compare_and_encrypt_mpc_script_path
from Oblivious_Database_Query_Scheme.getters import get_compare_and_reencrypt_mpc_script_path as compare_and_reencrypt_mpc_script_path

from Server.Utilities.server_utilities import Utilities


class Communicator(Utilities):
    """
        Establishes a secure communication channel between the server and client.
        Allowing them to send and receive json files.
    """
    def __init__(self):
        super().__init__()

        self.HEADER = 1024
        self.LISTEN_PORT = 5005
        self.HOST = 'localhost'
        self.ADDR = (self.HOST, self.LISTEN_PORT)
        self.CLIENT_ADDR = ('localhost', 5500)
        self.FORMAT = 'utf-8'

        self.DATABASE_PREPROCESSING_MESSAGE = '<DATABASE PRE-PROCESSING>'
        self.ENCRYPT_FILES_MESSAGE = '<ENCRYPT FILES>'
        self.REENCRYPT_FILES_MESSAGE = '<REENCRYPT FILES>'
        self.SENDING_INDICES_MESSAGE = '<SENDING INDICES>'
        self.SENDING_JSON_MESSAGE = '<SENDING JSON>'
        self.FILE_NAME_MESSAGE = '<FILE NAME>'
        self.FILE_CONTENTS_MESSAGE = '<FILE CONTENTS>'
        self.ENCRYPT_QUERY_MESSAGE = '<ENCRYPT QUERY>'
        self.DISCONNECT_MESSAGE = '<DISCONNECT>'
        self.END_FILE_MESSAGE = '<END FILE>'

        self.server_context = SSLContext(PROTOCOL_TLS_SERVER)
        self.server_context.load_cert_chain(certfile=server_networking_certificate_path(),
                                            keyfile=server_networking_key_path())
        self.client_context = SSLContext(PROTOCOL_TLS_CLIENT)
        self.client_context.load_verify_locations(client_networking_certificate_path())
        self.listen_host = self.server_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_side=True)
        self.listen_host.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.listen_host.settimeout(0.1)

        self.close = False
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

    def wait(self, connection):
        """

        """

        while (message := connection.recv(self.HEADER).decode(self.FORMAT).strip()) != self.DISCONNECT_MESSAGE:
            sleep(0.01)


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
                    file.close()

    def send_json(self, file_name, file_contents):
        """
            Sends a json file to an address.

            Parameters:
                - json_file (str) : The dictionary to be sent.
                - address (tuple(str, int)) : The address to send to.

            Returns:

        """

        send_host = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')

        send_host.connect(self.CLIENT_ADDR)
        send_host.send(self.add_padding(self.FILE_NAME_MESSAGE))
        send_host.send(self.add_padding(f'{file_name}'))
        send_host.send(self.add_padding(self.FILE_CONTENTS_MESSAGE))
        send_host.send(self.add_padding(f'{file_contents}'))
        send_host.send(self.add_padding(self.END_FILE_MESSAGE))
        send_host.send(self.add_padding(self.DISCONNECT_MESSAGE))
        send_host.close()

    def received_database_preprocessing_message(self, connection, address):
        """

        """

        self.database_preprocessing()

        connection.send(self.add_padding(self.DISCONNECT_MESSAGE))

    def MP_SPDZ_record_encryption(self, connection, address, MP_SPDZ_script_name: str):
        """

        """

        while True:
            message = connection.recv(self.HEADER).decode(self.FORMAT).strip()
            if message == self.SENDING_INDICES_MESSAGE:
                index_a = int(connection.recv(self.HEADER).decode(self.FORMAT).strip())
                index_b = int(connection.recv(self.HEADER).decode(self.FORMAT).strip())
                connection.send(self.add_padding(self.DISCONNECT_MESSAGE))
                break

        if index_a is not None and index_b is not None:
            self.retrieve_and_encrypt_files(index_a, index_b, MP_SPDZ_script_name)

    def received_encrypt_query_message(self, connection, address):
        """

        """

        connection.send(self.add_padding(self.DISCONNECT_MESSAGE))

        self.encrypt_query()

    def receive(self, connection, address):
        """

        """

        message = connection.recv(self.HEADER).decode(self.FORMAT).strip()
        if message == self.SENDING_JSON_MESSAGE:
            print(f'[RECEIVED] {message} from {address}')
            self.receive_json(connection, address)
        elif message == self.DATABASE_PREPROCESSING_MESSAGE:
            print(f'[RECEIVED] {message} from {address}')
            self.received_database_preprocessing_message(connection, address)
            connection.send(self.add_padding(self.DISCONNECT_MESSAGE))
        elif message == self.ENCRYPT_FILES_MESSAGE:
            self.MP_SPDZ_record_encryption(connection, address, compare_and_encrypt_mpc_script_path().stem)
        elif message == self.REENCRYPT_FILES_MESSAGE:
            self.MP_SPDZ_record_encryption(connection, address, compare_and_reencrypt_mpc_script_path().stem)
        elif message == self.ENCRYPT_QUERY_MESSAGE:
            print(f'[RECEIVED] {message} from {address}')
            self.received_encrypt_query_message(connection, address)

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
                self.receive(conn, addr)
            except timeout:
                continue
            except Exception as e:
                print(f'[SERVER ERROR] {e}')

    def kill(self):
        """
            Closes the communication.

            Parameters:
                -

            Returns:

        """

        self.close = True
        self.run_thread.join()
        print(f'[CLOSED] {self.ADDR}')
