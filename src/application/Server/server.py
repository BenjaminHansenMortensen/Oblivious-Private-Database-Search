""" Handling the communication with the client. """

# Imports.
from time import sleep
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
from application.getters import (get_number_of_dummy_items as
                                 number_of_dummy_items)
from application.getters import (get_server_networking_key_path as
                                 server_networking_key_path)
from application.getters import (get_server_networking_certificate_path as
                                 server_networking_certificate_path)
from application.getters import (get_client_networking_certificate_path as
                                 client_networking_certificate_path)
from application.getters import (get_sort_and_encrypt_with_circuit_mpc_script_path as
                                 sort_and_encrypt_with_circuit_mpc_script_path)
from application.getters import (get_sort_and_reencrypt_with_circuit_mpc_script_path as
                                 sort_and_reencrypt_with_circuit_mpc_script_path)
from application.getters import (get_server_encrypted_inverted_index_matrix_directory as
                                 encrypted_inverted_index_matrix_directory)

# Server utility imports.
from application.Server.Utilities.server_utilities import Utilities


class Communicator(Utilities):
    """
        Establishes a secure communication channel between the server and client.
    """

    def __init__(self) -> None:
        super().__init__()

        self.HEADER = 1024
        self.LISTEN_PORT = server_port()
        self.HOST = server_ip()
        self.ADDR = (self.HOST, self.LISTEN_PORT)
        self.CLIENT_ADDR = (client_ip(), client_port())
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
        self.records_preprocessing_finished = False

        return

    def wait_for_client(self) -> None:
        """
            Waiting for the client to connect, then receives if it should resume from previous pre-processing.

            Parameters:
                -

            Returns:
                :raises
                -
        """
    
        # Tries to send online message to the client.
        try:
            self.send_online_message()
        except ConnectionRefusedError:
            print(f'[CONNECTING] Waiting for the client.')
        
        # Waits until the client is online.
        while not self.client_online:
            sleep(0.1)
        
        # Sends online message and receives response on whether to resume form previous pre-processing or not.
        self.send_online_message()
        while self.is_semantic_search is None:
            sleep(0.1)
        while self.resume_from_previous_preprocessing is None:
            sleep(0.1)

        # If true resumes from previous pre-processing.
        if self.resume_from_previous_preprocessing:
            self.resume()

        print(f'[CONNECTED] Connected to the client.')

        return

    def send_online_message(self) -> None:
        """
            Sends online message to the client.

            Parameters:
                -

            Returns:
                :raises
                -
        """

        # Sends online message to the client.
        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM),
                                                     server_hostname=client_networking_certificate_path().stem)
        connection.connect(self.CLIENT_ADDR)
        connection.sendall(self.add_padding(self.ONLINE_MESSAGE))
        connection.shutdown(SHUT_WR)
        connection.close()

        return

    def wait_for_records_preprocessing(self) -> None:
        """
            Waits until the client is ready to start the records pre-processing.

            Parameters:
                -

            Returns:
                :raises
                -
        """

        # Waits until the pre-processing finished message is received from the client.
        while not self.records_preprocessing_finished:
            sleep(0.1)

        return

    def wait_for_client_shutdown(self) -> None:
        """
            Waits until the client shuts down.

            Parameters:
                -

            Returns:
                :raises
                -
        """

        # Waits until the shutdown message is received from the client.
        while self.client_online:
            sleep(1)

        return

    def wait_for_indexing(self) -> None:
        """
            Waits until the indexing is complete.

            Parameters:
                -

            Returns:
                :raises
                -
        """

        # Waits until the shutdown message is received from the client.
        while not self.indexing_finished:
            sleep(1)

        return

    def add_padding(self, message: str) -> bytes:
        """
            Encodes and adds the appropriate padding to a message to match the header size.

            Parameters:
                - message (str) : The message to be padded.

            Returns:
                :raises
                - message (bytes) : The padded message.
        """

        # Encodes the message and pads it with null bytes.
        message = message.encode(self.FORMAT)
        message += b'\x00' * (self.HEADER - len(message))

        return message

    def wait(self, connection: SSLSocket) -> None:
        """
            Waits until the disconnect message is received from the client.

            Parameters:
                - connection (SSLSocket) : Connection with the client.

            Returns:
                :raises
                -
        """

        # Waits until the disconnect message is received from the client.
        while (connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0))) != self.DISCONNECT_MESSAGE:
            sleep(0.01)

        return

    def send_number_of_dummy_items(self) -> None:
        """
            Sends the number of dummy items in the database to the client.

            Parameters:
                -

            Returns:
                :raises
                -
        """

        # Sends the amount of dummy items needed.
        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM),
                                                     server_hostname=client_networking_certificate_path().stem)
        connection.connect(self.CLIENT_ADDR)
        connection.sendall(self.add_padding(self.SENDING_NUMBER_OF_DUMMY_ITEMS))
        connection.sendall(self.add_padding(str(number_of_dummy_items())))
        print(f'[SENT] {self.SENDING_NUMBER_OF_DUMMY_ITEMS} to client.')

        self.wait(connection)
        connection.shutdown(SHUT_WR)
        connection.close()

        return

    def send_encrypted_inverted_index_matrix(self) -> None:
        """
            Sends the encrypted inverted index matrix to the client.

            Parameters:
                -

            Returns:
                :raises
                -
        """

        encrypted_inverted_index_matrix_part_paths = [path for path in
                                                      encrypted_inverted_index_matrix_directory().glob('*')]
        print(f'[SENT] {self.SENDING_ENCRYPTED_INVERTED_INDEX_MATRIX_MESSAGE} to client.')

        # Sends each part of the encrypted inverted index matrix to the client.
        for encrypted_inverted_index_matrix_part_path in encrypted_inverted_index_matrix_part_paths:
            connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM),
                                                         server_hostname=client_networking_certificate_path().stem)
            connection.connect(self.CLIENT_ADDR)
            connection.sendall(self.add_padding(self.SENDING_ENCRYPTED_INVERTED_INDEX_MATRIX_MESSAGE))

            # Reads the encrypted inverted index matrix.
            with encrypted_inverted_index_matrix_part_path.open('r') as f:
                encrypted_inverted_index_matrix_part = f.read()
                f.close()

            # Sends the encrypted inverted index matrix part to the client.
            message_bytes = str.encode(encrypted_inverted_index_matrix_part)
            for i in range(0, len(message_bytes), self.HEADER):
                connection.sendall(self.add_padding((message_bytes[i: i + self.HEADER]).decode(self.FORMAT)))
            connection.sendall(self.add_padding(self.END_FILE_MESSAGE))

            self.wait(connection)
            connection.shutdown(SHUT_WR)
            connection.close()

        # Sends the sending encrypted inverted index matrix finished message to the client.
        connection = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM),
                                                     server_hostname=client_networking_certificate_path().stem)
        connection.connect(self.CLIENT_ADDR)
        connection.sendall(self.add_padding(self.SENDING_ENCRYPTED_INVERTED_INDEX_MATRIX_FINISHED_MESSAGE))
        print(f'[SENT] {self.SENDING_ENCRYPTED_INVERTED_INDEX_MATRIX_FINISHED_MESSAGE} to client.')
        connection.shutdown(SHUT_WR)
        connection.close()

        return

    def received_records_preprocessing_message(self, connection: SSLSocket) -> None:
        """
            Performs the server side of the records pre-processing.

            Parameters:
                - connection (SSLSocket) : The connection with the client.

            Returns:
                :raises
                -
        """

        # Server side of the records pre-processing
        self.setup_and_encode_records()

        while (message := connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0))) != self.RECORDS_PREPROCESSING_FINISHED_MESSAGE:
            if message == self.ENCRYPT_RECORDS_MESSAGE:
                self.mp_spdz_record_encryption(connection, sort_and_encrypt_with_circuit_mpc_script_path().stem)
            elif message == self.REENCRYPT_RECORDS_MESSAGE:
                self.mp_spdz_record_encryption(connection, sort_and_reencrypt_with_circuit_mpc_script_path().stem)

        print(f'[RECEIVED] {message} from client.')
        self.write_encrypted_record_pointers()
        self.records_preprocessing_finished = True

        return

    def mp_spdz_record_encryption(self, connection: SSLSocket, mpc_script_name: str) -> None:
        """
            Obliviously encrypts, with the client's keys, two records of the client's choosing.

            Parameters:
                - connection (SSLSocket) : Connection with the client.
                - mp_spdz_script_name (str): Name of the .mpc script to be used.

            Returns:
                :raises ValueError
                -
        """

        # Receives two indices from the client.
        index_a = int(connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0)))
        index_b = int(connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0)))
        connection.sendall(self.add_padding(self.DISCONNECT_MESSAGE))

        # Obliviously encrypts the requested records, with the client's key.
        if index_a is not None and index_b is not None:
            address, port = self.ADDR
            self.encrypt_records(index_a, index_b, mpc_script_name, address)
        else:
            raise ValueError('The received indices are not valid.')

        return

    def create_semantic_indexing(self) -> None:
        """
            Creates a semantic indexing of the records.

            Parameters:
                -

            Returns:
                :raises
                -
        """
        print('[INDEXING] Creating the semantic indexing of the records.')
        self.semantic_indexing()

        print('[INDEXING FINISHED] Finished creating the semantic indexing.')
        self.indexing_finished = True

        return

    def received_semantic_search_message(self, connection: SSLSocket) -> None:
        """
            Obliviously compares the search query embedding to the embedding of each record.

            Parameters:
                - connection (SSLSocket) : Connection with the client.

            Returns:
                :raises
                -
        """

        # Closes the connection with the client.
        connection.sendall(self.add_padding(self.DISCONNECT_MESSAGE))

        # Runs the server side of the semantic search.
        address, port = self.CLIENT_ADDR
        self.semantic_search(address)

        return

    def received_encrypt_query_message(self, connection: SSLSocket) -> None:
        """
            Oblivious encrypts the client's search query under the server's key.

            Parameters:
                - connection (SSLSocket) : Connection with the client.

            Returns:
                :raises
                -
        """

        # Closes the connection with the client.
        connection.sendall(self.add_padding(self.DISCONNECT_MESSAGE))

        # Obliviously encrypts the client's search query with the server's key.
        address, port = self.CLIENT_ADDR
        self.encrypt_query(address)

        return

    def send_encrypted_record(self, connection: SSLSocket) -> None:
        """
            Sends a requested encrypted record to the client.

            Parameters:
                - connection (SSLSocket) : Connection with the client.

            Returns:
                :raises
                -
        """

        # Fetches the requested encrypted record.
        index = int(connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0)))
        encrypted_record_path = self.encrypted_record_pointers[index]
        with encrypted_record_path.open('r') as f:
            encrypted_record = f.read()
            f.close()

        # Sends the encrypted record to the client.
        connection.sendall(self.add_padding(encrypted_record))
        connection.sendall(self.add_padding(self.END_FILE_MESSAGE))

        return

    def receive(self, connection: SSLSocket) -> None:
        """
            Handling of received messages from the client.

            Parameters:
                - connection (SSLSocket) : Connection with the client.

            Returns:
                :raises
                -
        """

        # Receives a message from the client and handles it accordingly.
        message = connection.recv(self.HEADER).decode(self.FORMAT).strip(chr(0))
        if message == self.ONLINE_MESSAGE:
            print(f'[RECEIVED] {message} from client.')
            self.client_online = True
            self.is_semantic_search = eval(connection.recv(
                                           self.HEADER).decode(self.FORMAT).strip(chr(0)))
            self.resume_from_previous_preprocessing = eval(connection.recv(
                                                           self.HEADER).decode(self.FORMAT).strip(chr(0)))
        elif message == self.RECORDS_PREPROCESSING_MESSAGE:
            print(f'[RECEIVED] {message} from client.')
            self.received_records_preprocessing_message(connection)
        elif message == self.SEMANTIC_SEARCH_MESSAGE:
            self.wait_for_indexing()
            print(f'[RECEIVED] {message} from client.')
            self.received_semantic_search_message(connection)
        elif message == self.ENCRYPT_QUERY_MESSAGE:
            print(f'[RECEIVED] {message} from client.')
            self.received_encrypt_query_message(connection)
        elif message == self.REQUEST_ENCRYPTED_RECORD_MESSAGE:
            print(f'[RECEIVED] {message} from client.')
            self.send_encrypted_record(connection)
        elif message == self.SHUTDOWN_MESSAGE:
            print(f'[RECEIVED] {message} from client.')
            self.client_online = False

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

        # Binds the server to a socket and listens for connections.
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
            Closes the server.

            Parameters:
                -

            Returns:
                :raises
                -
        """

        # Closes all threads and processes associated with the server.
        self.close = True
        self.run_thread.join()
        print(f'[CLOSED] {self.ADDR}')

        return
