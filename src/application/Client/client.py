""" Handling the communication with the server. """

# Imports.
from time import sleep
from json import dump, loads
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, timeout, SHUT_WR
from ssl import SSLContext, PROTOCOL_TLS_CLIENT, PROTOCOL_TLS_SERVER, SSLSocket

# Local getter imports.
from application.getters import (get_server_ip as
                                 server_ip)
from application.getters import (get_server_port as
                                 server_port)
from application.getters import (get_client_ip as
                                 client_ip)
from application.getters import (get_client_port as
                                 client_port)
from application.getters import (get_client_networking_key_path as
                                 client_networking_key_path)
from application.getters import (get_client_networking_certificate_path as
                                 client_networking_certificate_path)
from application.getters import (get_server_networking_certificate_path as
                                 server_networking_certificate_path)
from application.getters import (get_client_encrypted_inverted_index_matrix_directory as
                                 encrypted_inverted_index_matrix_directory)
from application.getters import (get_client_number_of_dummy_items_path as
                                 number_of_dummy_items_path)


# Client utility imports.
from application.Client.Utilities.client_utilities import Utilities
from application.Client.Utilities.record_decryptor import run as decrypt_and_store_files

class Communicator(Utilities):
    """
        Establishes a secure communication channel between the client and server.
    """

    def __init__(self) -> None:
        super().__init__()
        self.HEADER = 1024
        self.LISTEN_PORT = client_port()
        self.HOST = client_ip()
        self.ADDR = (self.HOST, self.LISTEN_PORT)
        self.SERVER_ADDR = (server_ip(), server_port())
        self.FORMAT = 'utf-8'

        self.ONLINE_MESSAGE = '<ONLINE>'
        self.SENDING_NUMBER_OF_DUMMY_ITEMS = '<SENDING NUMBER OF DUMMY ITEMS>'
        self.RECORDS_PREPROCESSING_MESSAGE = '<RECORDS PRE-PROCESSING>'
        self.ENCRYPT_RECORDS_MESSAGE = '<ENCRYPT RECORDS>'
        self.REENCRYPT_RECORDS_MESSAGE = '<REENCRYPT RECORDS>'
        self.RECORDS_PREPROCESSING_FINISHED_MESSAGE = '<RECORDS PRE-PROCESSING FINISHED>'
        self.SENDING_ENCRYPTED_INVERTED_INDEX_MATRIX_MESSAGE = '<SENDING ENCRYPTED INVERTED INDEX MATRIX>'
        self.SENDING_ENCRYPTED_INVERTED_INDEX_MATRIX_FINISHED_MESSAGE = \
            '<SENDING ENCRYPTED INVERTED INDEX MATRIX FINISHED>'
        self.SEMANTIC_SEARCH_MESSAGE = '<SEMANTIC SEARCH>'
        self.ENCRYPT_QUERY_MESSAGE = '<ENCRYPT QUERY>'
        self.REQUEST_ENCRYPTED_RECORD_MESSAGE = '<REQUESTING ENCRYPTED RECORD>'
        self.DISCONNECT_MESSAGE = '<DISCONNECT>'
        self.END_FILE_MESSAGE = '<END FILE>'
        self.SHUTDOWN_MESSAGE = '<SHUTTING DOWN>'

        self.client_context = SSLContext(PROTOCOL_TLS_SERVER)
        self.client_context.load_cert_chain(certfile=client_networking_certificate_path(),
                                            keyfile=client_networking_key_path())
        self.server_context = SSLContext(PROTOCOL_TLS_CLIENT)
        self.server_context.load_verify_locations(server_networking_certificate_path())
        self.listen_host = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_side=True)
        self.listen_host.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.listen_host.settimeout(0.1)

        self.close = False
        self.run_thread = Thread(target=self.run)
        self.run_thread.start()

        self.server_online = False
        self.dummy_items_sent = False
        self.encrypted_inverted_index_matrix_part = 0
        self.encrypted_inverted_index_matrix_received = False

        return

    def user_response(self, semantic_search: str, resume_response: str) -> None:
        """
            Updates internal variable with the user's response with whether to continue from previous pre-processing.

            Parameters:
                - semantic_search (str) : Input from the user.
                - response (str) : Input from the user.

            Returns:
                :raises
                -
        """

        # Updates local variable of the client depending on answer from the inputs.
        if semantic_search == 'y':
            self.is_semantic_search = True
        else:
            self.is_semantic_search = False

        if resume_response == 'y':
            self.resume_from_previous_preprocessing = True
        else:
            self.resume_from_previous_preprocessing = False

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
            self.send_online_message_and_user_response()
        except ConnectionRefusedError:
            print(f'[CONNECTING] Waiting for the server.')
        
        # Waits until the server is online.
        while not self.server_online:
            sleep(0.1)

        # Sends online message and user response on whether to resume from previous pre-processing or not.
        self.send_online_message_and_user_response()

        self.resume()

        print(f'[CONNECTED] Connected to the server.')

        return

    def send_online_message_and_user_response(self) -> None:
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
        connection = self.server_context.wrap_socket(socket(AF_INET, SOCK_STREAM),
                                                     server_hostname=server_networking_certificate_path().stem)
        connection.connect(self.SERVER_ADDR)
        connection.sendall(self.add_padding(self.ONLINE_MESSAGE))
        connection.sendall(self.add_padding(str(self.is_semantic_search)))
        connection.sendall(self.add_padding(str(self.resume_from_previous_preprocessing)))
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

    def waiting_to_send_number_of_dummy_items(self) -> None:
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

    def receive_number_of_dummy_items(self, connection: SSLSocket) -> None:
        """
            Receives the number of dummy items in the database from the server.

            Parameters:
                - connection (SSLSocket) : Connection with the server.

            Returns:
                :raises
                -
        """
        
        # Receives and creates the requested amount of dummy items and sends them to the server.
        number_of_dummy_items = int(connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0)))
        connection.sendall(self.add_padding(self.DISCONNECT_MESSAGE))

        # Writes the number of dummy items to a file.
        with number_of_dummy_items_path().open('w') as f:
            f.write(str(number_of_dummy_items))
            f.close()
        
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

        # Receives a part of the encrypted inverted index matrix.
        encrypted_inverted_index_matrix_part = ''
        while (message := connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0))) != self.END_FILE_MESSAGE:
            encrypted_inverted_index_matrix_part += message

        # Writes a part of the encrypted inverted index matrix into its own file.
        with open(encrypted_inverted_index_matrix_directory() /
                  f'Encrypted_Inverted_Index{self.encrypted_inverted_index_matrix_part}.json', 'w') as f:
            dump(loads(encrypted_inverted_index_matrix_part), f, indent=4)
            f.close()

        connection.sendall(self.add_padding(self.DISCONNECT_MESSAGE))

        # Updates object variables.
        self.encrypted_inverted_index_matrix_part += 1

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
        connection = self.server_context.wrap_socket(socket(AF_INET, SOCK_STREAM),
                                                     server_hostname=server_networking_certificate_path().stem)
        connection.connect(self.SERVER_ADDR)
        connection.sendall(self.add_padding(self.RECORDS_PREPROCESSING_MESSAGE))
        print(f'[SENT] {self.RECORDS_PREPROCESSING_MESSAGE} to server.')

        # Performs the client side of the records pre-processing.
        self.records_preprocessing(self, connection)

        # Sends records preprocessing finished message to the server.
        connection.sendall(self.add_padding(self.RECORDS_PREPROCESSING_FINISHED_MESSAGE))
        print(f'[SENT] {self.RECORDS_PREPROCESSING_FINISHED_MESSAGE} to server.')

        # Waits until the server disconnects.
        connection.shutdown(SHUT_WR)
        connection.close()

        return

    def send_indices_and_encrypt(self, connection: SSLSocket, swap: bool, index_a: int, index_b: int) -> None:
        """
            Obliviously sorts and encrypts two of the server's records with the client's key.

            Parameters:
                - connection (SSLSocket) : Connection with the server.
                - swap (bool) : Indicator to whether the records should be swapped or not.
                - index_a (int) : Index to a server side pointer to a record.
                - index_b (int) : Index to a server side pointer to a record.
                - host_address (str) : The hostname of the party to host the MP-SPDZ execution.
                - connection (SSLSocket) : Connection with the server.

            Returns:
                :raises
                -
        """

        # Sends which two records should be considered.
        connection.sendall(self.add_padding(self.ENCRYPT_RECORDS_MESSAGE))
        connection.sendall(self.add_padding(str(index_a)))
        connection.sendall(self.add_padding(str(index_b)))

        # Obliviously encrypts and sorts the two of the server's records with the client's key.
        host_address = self.SERVER_ADDR[0]
        self.encrypt_records(swap, index_a, index_b, host_address)

        return

    def send_indices_and_reencrypt(self, connection: SSLSocket, swap: bool, index_a: int, index_b: int) -> None:
        """
            Obliviously sorts and re-encrypts two of the server's records with the client's key.

            Parameters:
                - connection (SSLSocket) : Connection with the server.
                - swap (bool) : Indicator to whether the records should be swapped or not.
                - index_a (int) : Index to a server side pointer to a record.
                - index_b (int) : Index to a server side pointer to a record.
                - host_address (str) : The hostname of the party to host the MP-SPDZ execution.
                - connection (SSLSocket) : Connection with the server.

            Returns:
                :raises
                -
        """

        # Sends which two records should be considered.
        connection.sendall(self.add_padding(self.REENCRYPT_RECORDS_MESSAGE))
        connection.sendall(self.add_padding(str(index_a)))
        connection.sendall(self.add_padding(str(index_b)))

        # Obliviously re-encrypts and sorts the two of the server's records with the client's key.
        host_address = self.SERVER_ADDR[0]
        self.reencrypt_records(swap, index_a, index_b, host_address)

        return

    def send_semantic_search_message(self, search_query: str) -> None:
        """
            Obliviously compares the search query embedding to the embedding of each record.

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
        connection = self.server_context.wrap_socket(socket(AF_INET, SOCK_STREAM),
                                                     server_hostname=server_networking_certificate_path().stem)
        connection.connect(self.SERVER_ADDR)
        connection.sendall(self.add_padding(self.SEMANTIC_SEARCH_MESSAGE))
        print(f'[SENT] {self.SEMANTIC_SEARCH_MESSAGE} to server.')

        # Waits until the server disconnects.
        self.wait(connection)
        connection.shutdown(SHUT_WR)
        connection.close()

        # Gets the embedding of the search query and sets it locally.
        self.get_search_query_embedding(search_query)

        # Runs the client side of the semantic search.
        address, port = self.ADDR
        self.semantic_search(address)

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
        connection = self.server_context.wrap_socket(socket(AF_INET, SOCK_STREAM),
                                                     server_hostname=server_networking_certificate_path().stem)
        connection.connect(self.SERVER_ADDR)
        connection.sendall(self.add_padding(self.ENCRYPT_QUERY_MESSAGE))
        print(f'[SENT] {self.ENCRYPT_QUERY_MESSAGE} to server.')
        
        # Waits until the server disconnects.
        self.wait(connection)
        connection.shutdown(SHUT_WR)
        connection.close()

        # Obliviously encrypts the search query with the server's key.
        address, port = self.ADDR
        self.encrypt_search_query(search_query, address)
        
        return 

    def request_records(self) -> None:
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
            encryption_keys = self.get_stored_key_stream(database_index)
            
            # Requests the encrypted record from the server.
            encrypted_records = self.request_encrypted_record(database_index)
            
            # Decrypts and stores the record.
            decrypt_and_store_files(encrypted_records, encryption_keys)
            
            # Updates the object variable requested pointers.
            self.requested_indices.add(str(index))
            
        # Requests dummy items.
        for _ in range(self.get_number_of_requests_to_make() - len(indices)):
            
            # Gets a random dummy item on the server.
            random_dummy_item_index = self.get_random_dummy_item_index()
            dummy_item_database_index = self.permuted_indices[random_dummy_item_index]

            # Requests the dummy item from the server.
            self.request_encrypted_record(dummy_item_database_index)

            # Updates the object variable requested pointers.
            self.requested_indices.add(str(random_dummy_item_index))
            
        return

    def request_encrypted_record(self, index: int) -> list[str]:
        """
            Requests an encrypted record from the server.

            Parameters:
                - index (int) : Index to the pointer of the encrypted record on the server.

            Returns:
                :raises
                - encrypted_record (list[str]) : Encrypted record from the server.
        """

        # Sends the pointer to the server.
        connection = self.server_context.wrap_socket(socket(AF_INET, SOCK_STREAM),
                                                     server_hostname=server_networking_certificate_path().stem)
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
        connection = self.server_context.wrap_socket(socket(AF_INET, SOCK_STREAM),
                                                     server_hostname=server_networking_certificate_path().stem)
        connection.connect(self.SERVER_ADDR)
        connection.sendall(self.add_padding(self.SHUTDOWN_MESSAGE))
        print(f'[SENT] {self.SHUTDOWN_MESSAGE} from server.')
        connection.shutdown(SHUT_WR)
        connection.close()
        
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
        elif message == self.SENDING_ENCRYPTED_INVERTED_INDEX_MATRIX_FINISHED_MESSAGE:
            print(f'[RECEIVED] {message} from server.')
            self.encrypted_inverted_index_matrix_received = True
        elif message == self.SENDING_NUMBER_OF_DUMMY_ITEMS:
            print(f'[RECEIVED] {message} from server.')
            self.receive_number_of_dummy_items(connection)
            
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
