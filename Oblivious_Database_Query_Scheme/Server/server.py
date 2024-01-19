""" Handling the communication with the client """

from time import sleep
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, timeout, SHUT_WR
from ssl import SSLContext, PROTOCOL_TLS_CLIENT, PROTOCOL_TLS_SERVER

from Oblivious_Database_Query_Scheme.getters import get_database_size as database_size
from Oblivious_Database_Query_Scheme.getters import get_number_of_PNR_records as number_of_PNR_records
from Oblivious_Database_Query_Scheme.getters import get_number_of_dummy_items as number_of_dummy_items
from Oblivious_Database_Query_Scheme.getters import get_server_networking_key_path as server_networking_key_path
from Oblivious_Database_Query_Scheme.getters import get_server_networking_certificate_path as server_networking_certificate_path
from Oblivious_Database_Query_Scheme.getters import get_client_networking_certificate_path as client_networking_certificate_path
from Oblivious_Database_Query_Scheme.getters import get_sort_and_encrypt_with_circuit_mpc_script_path as sort_and_encrypt_with_circuit_mpc_script_path
from Oblivious_Database_Query_Scheme.getters import get_sort_and_reencrypt_with_circuit_mpc_script_path as sort_and_reencrypt_with_circuit_mpc_script_path
from Oblivious_Database_Query_Scheme.getters import get_server_encrypted_inverted_index_matrix_path as encrypted_inverted_index_matrix_path
from Oblivious_Database_Query_Scheme.getters import get_encrypted_PNR_records_directory as encrypted_PNR_records_directory
from Oblivious_Database_Query_Scheme.getters import get_PNR_records_directory as PNR_records_directory

from Oblivious_Database_Query_Scheme.Server.Utilities.server_utilities import Utilities


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

        self.ONLINE_MESSAGE = '<ONLINE>'
        self.RESUME_FROM_PREVIOUS = '<RESUME FROM PREVIOUS>'
        self.REQUEST_DUMMY_ITEMS_MESSAGE = '<REQUESTING DUMMY ITEMS>'
        self.DATABASE_PREPROCESSING_MESSAGE = '<DATABASE PRE-PROCESSING>'
        self.ENCRYPT_FILES_MESSAGE = '<ENCRYPT FILES>'
        self.REENCRYPT_FILES_MESSAGE = '<REENCRYPT FILES>'
        self.DATABASE_PREPROCESSING_FINISHED_MESSAGE = '<DATABASE PRE-PROCESSING FINISHED>'
        self.SENDING_INDICES_MESSAGE = '<SENDING INDICES>'
        self.SENDING_ENCRYPTED_INDEXING_MESSAGE = '<SENDING ENCRYPTED INDEXING>'
        self.FILE_NAME_MESSAGE = '<FILE NAME>'
        self.FILE_CONTENTS_MESSAGE = '<FILE CONTENTS>'
        self.ENCRYPT_QUERY_MESSAGE = '<ENCRYPT QUERY>'
        self.REQUEST_ENCRYPTED_PNR_RECORD_MESSAGE = '<REQUESTING ENCRYPTED PNR RECORD>'
        self.DISCONNECT_MESSAGE = '<DISCONNECT>'
        self.END_FILE_MESSAGE = '<END FILE>'
        self.SHUTDOWN_MESSAGE = '<SHUTTING DOWN>'

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

        self.client_online = False
        self.resume_from_previous = None
        self.preprocessing_finished = False

    def wait_for_client(self):
        """

        """

        try:
            self.send_online_message()
        except ConnectionRefusedError:
            print(f'[CONNECTING] Waiting for the client.')

        while not self.client_online:
            sleep(0.1)

        self.send_online_message()

        while self.resume_from_previous is None:
            sleep(0.1)

        if self.resume_from_previous:
            self.resume()

        print(f'[CONNECTED] Connected to the client.')

    def send_online_message(self):
        """

        """

        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')
        connection.connect(self.CLIENT_ADDR)
        connection.sendall(self.add_padding(self.ONLINE_MESSAGE))
        connection.shutdown(SHUT_WR)
        connection.close()

    def wait_for_preprocessing(self):
        """

        """

        while not self.preprocessing_finished:
            sleep(0.1)

    def wait_for_client_shutdown(self):
        """

        """

        while self.client_online:
            sleep(1)


    def add_padding(self, message):
        """
            Encodes and adds the appropriate padding to a message to match the header size.

            Parameters:
                - message (str) : The message to be padded.

            Returns:
                message (bytes) : The padded message.
        """

        message = message.encode(self.FORMAT)
        message += b'\x00' * (self.HEADER - len(message))
        return message

    def wait(self, connection):
        """

        """

        while (message := connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0))) != self.DISCONNECT_MESSAGE:
            sleep(0.01)

    def create_database(self):
        """

        """

        self.generate_PNR_records()

    def request_dummy_items(self):
        """

        """

        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')
        connection.connect(self.CLIENT_ADDR)
        connection.sendall(self.add_padding(self.REQUEST_DUMMY_ITEMS_MESSAGE))
        connection.sendall(self.add_padding(str(number_of_dummy_items())))

        for i in range(number_of_PNR_records(), database_size()):
            dummy_item = ''
            while (message := connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0))) != self.END_FILE_MESSAGE:
                dummy_item += message

            file_path = PNR_records_directory() / f"{i}.txt"
            with file_path.open("w") as file:
                file.write(dummy_item)
                file.close()

            self.records_indexing.append(file_path)

        connection.shutdown(SHUT_WR)
        connection.close()


    def send_encrypted_indexing(self):
        """
            Sends a json file to an address.

            Parameters:
                - json_file (str) : The dictionary to be sent.
                - address (tuple(str, int)) : The address to send to.

            Returns:

        """

        file_name = encrypted_inverted_index_matrix_path().name
        with encrypted_inverted_index_matrix_path().open("r") as file:
            encrypted_inverted_index_matrix = file.read()
            file.close()

        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')
        connection.connect(self.CLIENT_ADDR)
        connection.sendall(self.add_padding(self.SENDING_ENCRYPTED_INDEXING_MESSAGE))
        print(f'[SENT] {self.SENDING_ENCRYPTED_INDEXING_MESSAGE} to client.')
        connection.sendall(self.add_padding(self.FILE_NAME_MESSAGE))
        connection.sendall(self.add_padding(file_name))
        connection.sendall(self.add_padding(self.FILE_CONTENTS_MESSAGE))
        connection.sendall(self.add_padding(encrypted_inverted_index_matrix))
        connection.sendall(self.add_padding(self.END_FILE_MESSAGE))
        connection.sendall(self.add_padding(self.DISCONNECT_MESSAGE))
        connection.shutdown(SHUT_WR)
        connection.close()

    def received_database_preprocessing_message(self, connection, address):
        """

        """

        self.database_preprocessing()

        connection.sendall(self.add_padding(self.DISCONNECT_MESSAGE))

    def MP_SPDZ_record_encryption(self, connection, address, MP_SPDZ_script_name: str):
        """

        """

        while True:
            message = connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0))
            if message == self.SENDING_INDICES_MESSAGE:
                index_a = int(connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0)))
                index_b = int(connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0)))
                connection.sendall(self.add_padding(self.DISCONNECT_MESSAGE))
                break

        if index_a is not None and index_b is not None:
            self.retrieve_and_encrypt_files(index_a, index_b, MP_SPDZ_script_name)

    def received_encrypt_query_message(self, connection, address):
        """

        """

        connection.sendall(self.add_padding(self.DISCONNECT_MESSAGE))

        self.encrypt_query()

    def send_encrypted_PNR_record(self, connection, address):
        """

        """

        index = connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0))
        encrypted_PNR_record_path = encrypted_PNR_records_directory() / f"{index}.txt"

        with encrypted_PNR_record_path.open("r") as file:
            encrypted_PNR_record = file.read()
            file.close()

        connection.sendall(self.add_padding(encrypted_PNR_record))
        connection.sendall(self.add_padding(self.END_FILE_MESSAGE))

    def receive(self, connection, address):
        """

        """

        message = connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0))
        if message == self.ONLINE_MESSAGE:
            self.client_online = True
            self.resume_from_previous = eval(connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0)))
        elif message == self.RESUME_FROM_PREVIOUS:
            self.resume_from_previous = True
        elif message == self.DATABASE_PREPROCESSING_MESSAGE:
            print(f'[RECEIVED] {message} from client.')
            self.received_database_preprocessing_message(connection, address)
            connection.sendall(self.add_padding(self.DISCONNECT_MESSAGE))
        elif message == self.DATABASE_PREPROCESSING_FINISHED_MESSAGE:
            print(f'[RECEIVED] {message} from client.')
            self.preprocessing_finished = True
        elif message == self.ENCRYPT_FILES_MESSAGE:
            self.MP_SPDZ_record_encryption(connection, address, sort_and_encrypt_with_circuit_mpc_script_path().stem)
        elif message == self.REENCRYPT_FILES_MESSAGE:
            self.MP_SPDZ_record_encryption(connection, address, sort_and_reencrypt_with_circuit_mpc_script_path().stem)
        elif message == self.ENCRYPT_QUERY_MESSAGE:
            print(f'[RECEIVED] {message} from client.')
            self.received_encrypt_query_message(connection, address)
        elif message == self.REQUEST_ENCRYPTED_PNR_RECORD_MESSAGE:
            print(f'[RECEIVED] {message} from client.')
            self.send_encrypted_PNR_record(connection, address)
        elif message == self.SHUTDOWN_MESSAGE:
            self.client_online = False

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
                self.listen_host.close()
                return

            try:
                conn, addr = self.listen_host.accept()
                self.receive(conn, addr)
            except timeout:
                continue

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
