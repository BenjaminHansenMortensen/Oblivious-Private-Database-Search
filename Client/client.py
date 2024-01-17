""" Handling the communication with the client """

from time import sleep
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, timeout, SHUT_WR
from ssl import SSLContext, PROTOCOL_TLS_CLIENT, PROTOCOL_TLS_SERVER

from Oblivious_Database_Query_Scheme.getters import get_client_networking_key_path as client_networking_key_path
from Oblivious_Database_Query_Scheme.getters import get_client_networking_certificate_path as client_networking_certificate_path
from Oblivious_Database_Query_Scheme.getters import get_server_networking_certificate_path as server_networking_certificate_path
from Oblivious_Database_Query_Scheme.getters import get_client_indexing_directory as indexing_directory
from Oblivious_Database_Query_Scheme.getters import get_records_encryption_key_streams_directory as encryption_key_streams_directory

from Client.Utilities.client_utilities import Utilities
from Client.Encoding.file_decryptor import run as decrypt_and_store_files
from Client.Preprocessing.key_stream_generator import get_key_streams


class Communicator(Utilities):
    """
        Establishes a secure communication channel between the server and client.
        Allowing them to send and receive json files.
    """
    def __init__(self):
        super().__init__()
        self.HEADER = 1024
        self.LISTEN_PORT = 5500
        self.HOST = 'localhost'
        self.ADDR = (self.HOST, self.LISTEN_PORT)
        self.SERVER_ADDR = ('localhost', 5005)
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
        self.server_context.load_cert_chain(certfile=client_networking_certificate_path(),
                                            keyfile=client_networking_key_path())
        self.client_context = SSLContext(PROTOCOL_TLS_CLIENT)
        self.client_context.load_verify_locations(server_networking_certificate_path())
        self.listen_host = self.server_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_side=True)
        self.listen_host.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.listen_host.settimeout(0.1)

        self.close = False
        self.run_thread = Thread(target=self.run)
        self.run_thread.start()

        self.server_online = False
        self.resume_from_previous = False
        self.encrypted_indexing_received = False

    def wait_for_server(self):
        """

        """

        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')

        try:
            connection.connect(self.SERVER_ADDR)
            connection.sendall(self.add_padding(self.ONLINE_MESSAGE))
            self.server_online = True
        except ConnectionRefusedError:
            print(f'[CONNECTING] Waiting for the server.')

        while not self.server_online:
            sleep(0.1)

        connection.sendall(self.add_padding(str(self.resume_from_previous)))
        connection.shutdown(SHUT_WR)
        connection.close()

        if self.resume_from_previous:
            self.resume()

        print(f'[CONNECTED] Connected to the server.')

    def send_resume_message(self):
        """

        """

        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')
        connection.connect(self.SERVER_ADDR)
        connection.sendall(self.add_padding(self.RESUME_FROM_PREVIOUS))
        connection.shutdown(SHUT_WR)
        connection.close()

    def wait_for_encrypted_indexing(self):
        """

        """

        while not self.encrypted_indexing_received:
            sleep(0.1)

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

    def send_dummy_items(self, connection, address):
        """

        """
        number_of_dummy_items = int(connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0)))
        for i in range(number_of_dummy_items):
            dummy_item = " ".join(get_key_streams())
            connection.sendall(self.add_padding(dummy_item))
            connection.sendall(self.add_padding(self.END_FILE_MESSAGE))

        connection.sendall(self.add_padding(self.DISCONNECT_MESSAGE))

    def receive_encrypted_indexing(self, connection, address):
        """
            Receives the json file and writes it.

            Parameters:
                - connection (socket) : The connection to the sender.
                - address (tuple(str, int)) : The address to receive from.

            Returns:

        """

        while True:
            message = connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0))
            if message == self.DISCONNECT_MESSAGE:
                self.encrypted_indexing_received = True
                return
            elif message == self.FILE_NAME_MESSAGE:
                file_name = connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0))
            elif message == self.FILE_CONTENTS_MESSAGE:
                file_contents = ''
                while (message := connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0))) != self.END_FILE_MESSAGE:
                    file_contents += message

                file_path = indexing_directory() / file_name
                with file_path.open("w") as file:
                    file.write(file_contents)
                    file.close()

                self.encrypted_indexing = eval(file_contents)

    def send_database_preprocessing_message(self):
        """

        """

        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')
        connection.connect(self.SERVER_ADDR)
        connection.sendall(self.add_padding(self.DATABASE_PREPROCESSING_MESSAGE))
        print(f'[SENT] {self.DATABASE_PREPROCESSING_MESSAGE} to server.')
        self.wait(connection)
        connection.shutdown(SHUT_WR)
        connection.close()

        self.database_preprocessing(self)
        self.send_preprocessing_finished_message()

    def send_indices_and_encrypt(self, swap: bool, index_a: int, index_b: int):
        """

        """

        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')
        connection.connect(self.SERVER_ADDR)
        connection.sendall(self.add_padding(self.ENCRYPT_FILES_MESSAGE))
        connection.sendall(self.add_padding(self.SENDING_INDICES_MESSAGE))
        connection.sendall(self.add_padding(str(index_a)))
        connection.sendall(self.add_padding(str(index_b)))
        self.wait(connection)
        connection.shutdown(SHUT_WR)
        connection.close()

        self.encrypt_files(swap, index_a, index_b)

    def send_indices_and_reencrypt(self, swap: bool, index_a: int, index_b: int):
        """

        """

        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')
        connection.connect(self.SERVER_ADDR)
        connection.sendall(self.add_padding(self.REENCRYPT_FILES_MESSAGE))
        connection.sendall(self.add_padding(self.SENDING_INDICES_MESSAGE))
        connection.sendall(self.add_padding(str(index_a)))
        connection.sendall(self.add_padding(str(index_b)))
        self.wait(connection)
        connection.shutdown(SHUT_WR)
        connection.close()

        self.reencrypt_files(swap, index_a, index_b)

    def send_preprocessing_finished_message(self):
        """

        """

        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')
        connection.connect(self.SERVER_ADDR)
        connection.sendall(self.add_padding(self.DATABASE_PREPROCESSING_FINISHED_MESSAGE))
        print(f'[SENT] {self.DATABASE_PREPROCESSING_FINISHED_MESSAGE} to server.')
        connection.shutdown(SHUT_WR)
        connection.close()

    def send_encrypt_query_message(self, search_query: str):
        """

        """

        if self.get_number_of_requests_to_make() > len(self.dummy_items_indices):
            self.kill()
            raise Exception("Insufficient amount of dummy items. Please redo pre-processing of the database.")

        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')
        connection.connect(self.SERVER_ADDR)
        connection.sendall(self.add_padding(self.ENCRYPT_QUERY_MESSAGE))
        print(f'[SENT] {self.ENCRYPT_QUERY_MESSAGE} to server.')
        self.wait(connection)
        connection.shutdown(SHUT_WR)
        connection.close()

        self.encrypt_search_query(search_query)

    def request_PNR_records(self):
        """

        """

        pointers = self.get_pointers()

        for pointer in pointers:
            database_index = self.permuted_index[pointer]

            encryption_key_streams = self.get_record_key_streams(database_index)

            encrypted_PNR_records = self.request_encrypted_PNR_record(database_index)

            decrypt_and_store_files([encrypted_PNR_records], [encryption_key_streams])

            self.requested_pointers.add(str(pointer))

        for _ in range(self.get_number_of_requests_to_make() - len(pointers)):
            random_dummy_item_index = self.get_random_dummy_item_index()
            dummy_item_database_index = self.permuted_index[random_dummy_item_index]

            self.request_encrypted_PNR_record(dummy_item_database_index)

            self.requested_pointers.add(str(random_dummy_item_index))

    def request_encrypted_PNR_record(self, index: int) -> list[str]:
        """
        
        """
        
        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')
        connection.connect(self.SERVER_ADDR)
        connection.sendall(self.add_padding(self.REQUEST_ENCRYPTED_PNR_RECORD_MESSAGE))
        print(f'[SENT] {self.REQUEST_ENCRYPTED_PNR_RECORD_MESSAGE} to server.')
        connection.sendall(self.add_padding(str(index)))
        ciphertexts = ''
        while (message := connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0))) != self.END_FILE_MESSAGE:
            ciphertexts += message

        connection.shutdown(SHUT_WR)
        connection.close()

        return ciphertexts.split(" ")

    def get_record_key_streams(self, index: str) -> list[str]:
        """

        """

        key_streams_path = encryption_key_streams_directory() / f"{index}.txt"
        with key_streams_path.open("r") as file:
            encryption_key_streams = file.read().split(" ")
            file.close()

        return encryption_key_streams

    def send_shutdown_message(self):
        """

        """

        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')
        connection.connect(self.SERVER_ADDR)
        connection.sendall(self.add_padding(self.SHUTDOWN_MESSAGE))
        connection.shutdown(SHUT_WR)
        connection.close()

    def receive(self, connection, address):
        """

        """

        message = connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0))
        print(f'[RECEIVED] {message} from server')
        if message == self.ONLINE_MESSAGE:
            self.server_online = True
        elif message == self.SENDING_ENCRYPTED_INDEXING_MESSAGE:
            self.receive_encrypted_indexing(connection, address)
        elif message == self.REQUEST_DUMMY_ITEMS_MESSAGE:
            self.send_dummy_items(connection, address)

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

        self.write_requested_pointers()
        self.send_shutdown_message()
        self.close = True
        self.run_thread.join()
        print(f'[CLOSED] {self.ADDR}')
