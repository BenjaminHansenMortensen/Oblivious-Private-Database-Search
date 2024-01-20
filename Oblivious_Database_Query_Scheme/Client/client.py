""" Handling the communication with the server. """

# Imports.
from time import sleep
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, timeout, SHUT_WR
from ssl import SSLContext, PROTOCOL_TLS_CLIENT, PROTOCOL_TLS_SERVER, SSLSocket

# Local getters imports.
from Oblivious_Database_Query_Scheme.getters import (get_client_networking_key_path as
                                                     client_networking_key_path)
from Oblivious_Database_Query_Scheme.getters import (get_client_networking_certificate_path as
                                                     client_networking_certificate_path)
from Oblivious_Database_Query_Scheme.getters import (get_server_networking_certificate_path as
                                                     server_networking_certificate_path)
from Oblivious_Database_Query_Scheme.getters import (get_client_encrypted_inverted_index_matrix_path as
                                                     encrypted_inverted_index_matrix_path)
from Oblivious_Database_Query_Scheme.getters import (get_records_encryption_key_streams_directory as
                                                     encryption_key_streams_directory)

# Client utility imports.
from Oblivious_Database_Query_Scheme.Client.Utilities.client_utilities import Utilities
from Oblivious_Database_Query_Scheme.Client.Utilities.record_decryptor import run as decrypt_and_store_files
from Oblivious_Database_Query_Scheme.Client.Utilities.key_stream_generator import get_key_streams


class Communicator(Utilities):
    """
        Establishes a secure communication channel between the client and server.
    """

    def __init__(self) -> None:
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
        self.RECORDS_PREPROCESSING_MESSAGE = '<RECORDS PRE-PROCESSING>'
        self.ENCRYPT_RECORDS_MESSAGE = '<ENCRYPT RECORDS>'
        self.REENCRYPT_RECORDS_MESSAGE = '<REENCRYPT RECORDS>'
        self.RECORDS_PREPROCESSING_FINISHED_MESSAGE = '<RECORDS PRE-PROCESSING FINISHED>'
        self.SENDING_ENCRYPTED_INVERTED_INDEX_MATRIX_MESSAGE = '<SENDING ENCRYPTED INVERTED INDEX MATRIX>'
        self.ENCRYPT_QUERY_MESSAGE = '<ENCRYPT QUERY>'
        self.REQUEST_ENCRYPTED_RECORD_MESSAGE = '<REQUESTING ENCRYPTED RECORD>'
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
        self.resume_from_previous_preprocessing = False
        self.dummy_items_sent = False
        self.encrypted_inverted_index_matrix_received = False

        return

    def wait_for_server(self) -> None:
        """
            Waiting for the server to connect, then sends if it should resume from previous pre-processing.

            Parameters:
                -

            Returns:
                :raises
                -
        """
        
        # Tries to send online message to the server.
        try:
            self.send_online_message_and_resume_boolean()
        except ConnectionRefusedError:
            print(f'[CONNECTING] Waiting for the server.')
        
        # Waits until the server is online.
        while not self.server_online:
            sleep(0.1)

        # Sends online message and user response on whether to resume from previous pre-processing or not.
        self.send_online_message_and_resume_boolean()
        
        if self.resume_from_previous_preprocessing:
            self.resume()

        print(f'[CONNECTED] Connected to the server.')

        return

    def send_online_message_and_resume_boolean(self) -> None:
        """
            Sends online message to the server together with the resume from previous preprocessing response from
            the user.

            Parameters:
                -

            Returns:
                :raises
                -
        """

        # Sends the online message to the server.
        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')
        connection.connect(self.SERVER_ADDR)
        connection.sendall(self.add_padding(self.ONLINE_MESSAGE))
        connection.sendall(self.add_padding(str(self.resume_from_previous_preprocessing)))
        connection.shutdown(SHUT_WR)
        connection.close()

        return

    def send_resume_message(self) -> None:
        """
            Sends the user's response on whether to resume from previous pre-processing or not.

            Parameters:
                -

            Returns:
                :raises
                -
        """

        # Sends the user's response to if it wants to continue from the previous pre-processing to the server..
        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')
        connection.connect(self.SERVER_ADDR)
        connection.sendall(self.add_padding(self.RESUME_FROM_PREVIOUS))
        connection.shutdown(SHUT_WR)
        connection.close()
        
        return 

    def add_padding(self, message: str) -> bytes:
        """
            Encodes and adds the appropriate padding to a message to match the header size.

            Parameters:
                - message (str) : The message to be padded.

            Returns:
                message (bytes) : The padded message.
        """

        # Encodes and pads the message with null bytes.
        message = message.encode(self.FORMAT)
        message += b'\x00' * (self.HEADER - len(message))
        
        return message

    def wait(self, connection: SSLSocket) -> None:
        """
            Waits until the disconnect message is received from the server.

            Parameters:
                - connection (SSLSocket) : Connection with the server.

            Returns:
                :raises
                -
        """

        # Waits until the disconnect message is received from the server.
        while (connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0))) != self.DISCONNECT_MESSAGE:
            sleep(0.01)
            
        return 

    def waiting_to_send_dummy_items(self) -> None:
        """
            Waits until the server requests dummy items.

            Parameters:
                -

            Returns:
                :raises
                -
        """

        # Waits until the requesting dummy items message is received from the server.
        while not self.dummy_items_sent:
            sleep(0.1)
            
        return 

    def send_dummy_items(self, connection: SSLSocket) -> None:
        """
            Receives the amount of dummy items requested, then creates them and sends them to the server.

            Parameters:
                - connection (SSLSocket) : Connection with the server.

            Returns:
                :raises
                -
        """
        
        # Receives and creates the requested amount of dummy items and sends them to the server.
        number_of_dummy_items = int(connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0)))
        for i in range(number_of_dummy_items):
            dummy_item = ' '.join(get_key_streams())
            connection.sendall(self.add_padding(dummy_item))
            connection.sendall(self.add_padding(self.END_FILE_MESSAGE))
        
        connection.sendall(self.add_padding(self.DISCONNECT_MESSAGE))
        
        # Updates internal values.
        self.number_of_dummy_items = number_of_dummy_items
        self.dummy_items_sent = True
        
        return 

    def wait_for_encrypted_inverted_index_matrix(self) -> None:
        """
            Waits until the encrypted inverted index matrix message is received.

            Parameters:
                -

            Returns:
                :raises
                -
        """

        # Waits until the sending encrypted inverted index matrix message is received from the server.
        while not self.encrypted_inverted_index_matrix_received:
            sleep(0.1)
            
        return 

    def receive_encrypted_inverted_index_matrix(self, connection: SSLSocket) -> None:
        """
            Receives the encrypted inverted index matrix and stores it.

            Parameters:
                - connection (SSLSocket) : Connection with the server.

            Returns:
                :raises
                -
        """

        # Receives the contents
        file_contents = ''
        while (message := connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0))) != self.END_FILE_MESSAGE:
            file_contents += message
                
        # Writes the inverted index matrix.
        with encrypted_inverted_index_matrix_path().open('w') as f:
            f.write(file_contents)
            f.close()

        # Updates object variables.
        self.encrypted_inverted_index_matrix_received = True
        self.encrypted_inverted_index_matrix = eval(file_contents)

        return

    def send_records_preprocessing_message(self) -> None:
        """
            Initiates the records pre-processing and performs the client side of it.

            Parameters:
                -

            Returns:
                :raises
                -
        """
        
        # Sends pre-processing message to the server.
        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')
        connection.connect(self.SERVER_ADDR)
        connection.sendall(self.add_padding(self.RECORDS_PREPROCESSING_MESSAGE))
        print(f'[SENT] {self.RECORDS_PREPROCESSING_MESSAGE} to server.')
        
        # Waits until the server disconnects.
        self.wait(connection)
        connection.shutdown(SHUT_WR)
        connection.close()

        # Performs the client side of the records pre-processing.
        self.database_preprocessing(self)
        self.send_records_preprocessing_finished_message()
        
        return 

    def send_indices_and_encrypt(self, swap: bool, index_a: int, index_b: int) -> None:
        """
            Obliviously sorts and encrypts two of the server's records with the client's key.

            Parameters:
                - swap (bool) : Indicator to whether the records should be swapped or not.
                - index_a (int) : Index to a server side pointer to a record.
                - index_b (int) : Index to a server side pointer to a record.

            Returns:
                :raises
                -
        """
        
        # Sends which two records should be considered.
        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')
        connection.connect(self.SERVER_ADDR)
        connection.sendall(self.add_padding(self.ENCRYPT_RECORDS_MESSAGE))
        connection.sendall(self.add_padding(str(index_a)))
        connection.sendall(self.add_padding(str(index_b)))
        
        # Waits until the server disconnects.
        self.wait(connection)
        connection.shutdown(SHUT_WR)
        connection.close()

        # Obliviously encrypts and sorts the two of the server's records with the client's key.
        self.encrypt_records(swap, index_a, index_b)
        
        return 

    def send_indices_and_reencrypt(self, swap: bool, index_a: int, index_b: int) -> None:
        """
            Obliviously sorts and re-encrypts two of the server's records with the client's key.

            Parameters:
                - swap (bool) : Indicator to whether the records should be swapped or not.
                - index_a (int) : Index to a server side pointer to a record.
                - index_b (int) : Index to a server side pointer to a record.
                
            Returns:
                :raises
                -
        """

        # Sends which two records should be considered.
        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')
        connection.connect(self.SERVER_ADDR)
        connection.sendall(self.add_padding(self.REENCRYPT_RECORDS_MESSAGE))
        connection.sendall(self.add_padding(str(index_a)))
        connection.sendall(self.add_padding(str(index_b)))
        
        # Waits until the server disconnects.
        self.wait(connection)
        connection.shutdown(SHUT_WR)
        connection.close()

        # Obliviously re-encrypts and sorts the two of the server's records with the client's key.
        self.reencrypt_records(swap, index_a, index_b)
        
        return 

    def send_records_preprocessing_finished_message(self) -> None:
        """
            Sends that the records preprocessing is finished ot the server.

            Parameters:
                -

            Returns:
                :raises
                -
        """
        
        # Sends records preprocessing finished message to the server.
        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')
        connection.connect(self.SERVER_ADDR)
        connection.sendall(self.add_padding(self.RECORDS_PREPROCESSING_FINISHED_MESSAGE))
        print(f'[SENT] {self.RECORDS_PREPROCESSING_FINISHED_MESSAGE} to server.')
        connection.shutdown(SHUT_WR)
        connection.close()
        
        return 

    def send_encrypt_query_message(self, search_query: str) -> None:
        """
            Obliviously sorts and re-encrypts two of the server's records with the client's key.

            Parameters:
                - search_query (str) : Search query from the user.

            Returns:
                :raises
                -
        """
        
        # Validates the there are enough unrequested dummy items left.
        if self.get_number_of_requests_to_make() > len(self.dummy_item_indices):
            self.kill()
            raise Exception('Insufficient amount of dummy items. Please redo pre-processing of the database.')
        
        # Sends search query to the server.
        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')
        connection.connect(self.SERVER_ADDR)
        connection.sendall(self.add_padding(self.ENCRYPT_QUERY_MESSAGE))
        print(f'[SENT] {self.ENCRYPT_QUERY_MESSAGE} to server.')
        
        # Waits until the server disconnects.
        self.wait(connection)
        connection.shutdown(SHUT_WR)
        connection.close()

        # Obliviously encrypts the search query with the server's key.
        self.encrypt_search_query(search_query)
        
        return 

    def request_pnr_records(self) -> None:
        """
            Obliviously sorts and re-encrypts two of the server's records with the client's key.

            Parameters:
                -

            Returns:
                :raises
                -
        """
        
        # Gets the result from the search.
        indices = self.get_indices()
        
        # Requests each record for each pointer of the indices.
        for index in indices:
            
            # Gets the server side index of the pointer to a record.
            database_index = self.permuted_indices[index]
            
            # Gets the corresponding encryption key streams.
            encryption_key_streams = self.get_record_key_streams(str(database_index))
            
            # Requests the encrypted record from the server.
            encrypted_records = self.request_encrypted_record(str(database_index))
            
            # Decrypts and stores the record.
            decrypt_and_store_files([encrypted_records], [encryption_key_streams])
            
            # Updates the object variable requested pointers.
            self.requested_indices.add(str(index))
            
        # Requests dummy items.
        for _ in range(self.get_number_of_requests_to_make() - len(indices)):
            
            # Gets a random dummy item on the server.
            random_dummy_item_index = self.get_random_dummy_item_index()
            dummy_item_database_index = self.permuted_indices[random_dummy_item_index]

            # Requests the dummy item from the server.
            self.request_encrypted_record(str(dummy_item_database_index))

            # Updates the object variable requested pointers.
            self.requested_indices.add(str(random_dummy_item_index))
            
        return

    def request_encrypted_record(self, index: str) -> list[str]:
        """
            Requests an encrypted record from the server.

            Parameters:
                - index (str) : Index to the pointer of the encrypted record on the server.

            Returns:
                :raises
                - encrypted_record (list[str]) : Encrypted record from the server.
        """
        
        # Sends the pointer to the server.
        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')
        connection.connect(self.SERVER_ADDR)
        connection.sendall(self.add_padding(self.REQUEST_ENCRYPTED_RECORD_MESSAGE))
        print(f'[SENT] {self.REQUEST_ENCRYPTED_RECORD_MESSAGE} to server.')
        connection.sendall(self.add_padding(str(index)))
        
        # Receives the encrypted record.
        encrypted_record = ''
        while (message := connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0))) != self.END_FILE_MESSAGE:
            encrypted_record += message

        connection.shutdown(SHUT_WR)
        connection.close()

        return encrypted_record.split(' ')

    @staticmethod
    def get_record_key_streams(index: str) -> list[str]:
        """
            Gets the corresponding key streams to a index.

            Parameters:
                - index (str) : Index to the pointer of the encryption key stream of the record.

            Returns:
                :raises
                - encryption_key_streams (list[str]) : Key streams to the encrypted record.
        """
        
        # Reads the encryption key streams.
        key_streams_path = encryption_key_streams_directory() / f'{index}.txt'
        with key_streams_path.open('r') as f:
            encryption_key_streams = f.read().split(' ')
            f.close()

        return encryption_key_streams

    def send_shutdown_message(self) -> None:
        """
            Sends the shutdown message to the server.

            Parameters:
                -

            Returns:
                :raises
                -
        """
        
        # Sends the shutdown message.
        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')
        connection.connect(self.SERVER_ADDR)
        connection.sendall(self.add_padding(self.SHUTDOWN_MESSAGE))
        connection.shutdown(SHUT_WR)
        connection.close()

        print(f'[SENT] {self.SHUTDOWN_MESSAGE} from server.')
        
        return 

    def receive(self, connection: SSLSocket) -> None:
        """
            Handling of received messages from the server.
            
            Parameters:
                - connection (SSLSocket) : Connection with the server.

            Returns:
                :raises
                -
        """

        # Receives a message from the server and handles it accordingly.
        message = connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0))
        if message == self.ONLINE_MESSAGE:
            print(f'[RECEIVED] {message} from server.')
            self.server_online = True
        elif message == self.SENDING_ENCRYPTED_INVERTED_INDEX_MATRIX_MESSAGE:
            self.receive_encrypted_inverted_index_matrix(connection)
        elif message == self.REQUEST_DUMMY_ITEMS_MESSAGE:
            print(f'[RECEIVED] {message} from server.')
            self.send_dummy_items(connection)
            
        return 

    def run(self) -> None:
        """
            Starts the listening and handles incoming connections.

            Parameters:
                -

            Returns:
                :raises
                - 
        """

        # Binds the client to a socket and listens for connections.
        self.listen_host.bind(self.ADDR)
        self.listen_host.listen()
        print(f'[LISTENING] on (\'{self.HOST}\', {self.LISTEN_PORT})')
        while True:
            if self.close:
                self.listen_host.close()
                return

            try:
                connection, address = self.listen_host.accept()
                self.receive(connection)
            except timeout:
                continue

    def kill(self) -> None:
        """
            Closes the client.

            Parameters:
                -

            Returns:
                :raises
                -
        """

        # Closes all threads and processes associated with the client.
        self.write_requested_indices()
        self.send_shutdown_message()
        self.close = True
        self.run_thread.join()
        print(f'[CLOSED] {self.ADDR}')
        
        return 
