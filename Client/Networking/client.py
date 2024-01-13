""" Handling the communication with the client """

from time import sleep
from os import chdir
from re import findall
from subprocess import Popen, PIPE
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, timeout
from ssl import SSLContext, PROTOCOL_TLS_CLIENT, PROTOCOL_TLS_SERVER
from hashlib import shake_128

from Oblivious_Database_Query_Scheme.getters import get_database_size as database_size
from Oblivious_Database_Query_Scheme.getters import get_block_size as block_size
from Oblivious_Database_Query_Scheme.getters import get_encoding_base as encoding_base
from Oblivious_Database_Query_Scheme.getters import get_client_MP_SPDZ_input_path as MP_SPDZ_input_path
from Oblivious_Database_Query_Scheme.getters import get_client_MP_SPDZ_output_path as MP_SPDZ_output_path
from Oblivious_Database_Query_Scheme.getters import get_working_directory as working_directory
from Oblivious_Database_Query_Scheme.getters import get_MP_SPDZ_directory as MP_SPDZ_directory
from Oblivious_Database_Query_Scheme.getters import get_number_of_bytes as number_of_bytes
from Oblivious_Database_Query_Scheme.getters import get_compare_and_encrypt_mpc_script_path as compare_and_encrypt_mpc_script_path
from Oblivious_Database_Query_Scheme.getters import get_compare_and_reencrypt_mpc_script_path as compare_and_reencrypt_mpc_script_path
from Oblivious_Database_Query_Scheme.getters import get_aes_128_mpc_script_path as aes_128_mpc_script_path
from Oblivious_Database_Query_Scheme.getters import get_records_encryption_key_streams_directory as encryption_keys_directory


from Client.Preprocessing.key_stream_generator import get_key_streams



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

        self.INIT_MESSAGE = '<PRE-PROCESSING>'
        self.ENCRYPT_EXECUTION_MESSAGE = '<ENCRYPT EXECUTION>'
        self.REENCRYPT_EXECUTION_MESSAGE = '<REENCRYPT EXECUTION>'
        self.SENDING_INDICES_MESSAGE = '<SENDING INDICES>'
        self.SENDING_JSON_MESSAGE = '<SENDING JSON>'
        self.FILE_NAME_MESSAGE = '<FILE NAME>'
        self.FILE_CONTENTS_MESSAGE = '<FILE CONTENTS>'
        self.ENCRYPT_QUERY = '<ENCRYPT QUERY>'
        self.DISCONNECT_MESSAGE = '<DISCONNECT>'
        self.END_FILE_MESSAGE = '<END FILE>'

        self.server_context = SSLContext(PROTOCOL_TLS_SERVER)
        self.server_context.load_cert_chain(certfile='Client/Networking/Keys/cert.pem', keyfile='Client/Networking/Keys/key.pem')
        self.client_context = SSLContext(PROTOCOL_TLS_CLIENT)
        self.client_context.load_verify_locations('Server/Networking/Keys/cert.pem')
        self.listen_host = self.server_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_side=True)
        self.listen_host.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.listen_host.settimeout(0.1)

        self.key_streams = []

        self.close = False
        self.run_thread = Thread(target=self.run)
        self.run_thread.start()

    def receive(self, connection, address):
        """

        """

        message = connection.recv(self.HEADER).decode(self.FORMAT).strip()
        print(f'[RECEIVED] {message} from {address}')
        if message == self.SENDING_JSON_MESSAGE:
            self.receive_json(connection, address)

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

        send_host.connect(self.SERVER_ADDR)
        send_host.send(self.add_padding(self.FILE_NAME_MESSAGE))
        send_host.send(self.add_padding(f'{file_name}'))
        send_host.send(self.add_padding(self.FILE_CONTENTS_MESSAGE))
        send_host.send(self.add_padding(f'{file_contents}'))
        send_host.send(self.add_padding(self.END_FILE_MESSAGE))
        send_host.send(self.add_padding(self.DISCONNECT_MESSAGE))
        send_host.close()

    def send_query(self, search_query: str) -> str:
        """

        """

        send_host = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')

        send_host.connect(self.SERVER_ADDR)
        send_host.send(self.add_padding(self.ENCRYPT_QUERY))
        self.wait(send_host)
        send_host.close()

        query_digest = shake_128(search_query.encode('ASCII')).digest(number_of_bytes()).hex()
        self.write_as_MP_SPDZ_inputs(0, [[query_digest]])
        self.run_MP_SPDZ(aes_128_mpc_script_path().stem, 0)
        encrypted_query = self.get_MP_SPDZ_output(0)

        return encrypted_query

    def get_MP_SPDZ_output(self, player_id: int) -> str:
        """

        """

        with open(MP_SPDZ_output_path().parent / f"{MP_SPDZ_output_path()}-P{player_id}-0", 'r') as file:
            hexadecimals_pattern = r"0x([a-fA-F0-9]+)"
            encrypted_query = findall(hexadecimals_pattern, file.read())
        return encrypted_query[0]

    def wait(self, connection):
        """

        """

        while (message := connection.recv(self.HEADER).decode(self.FORMAT).strip()) != self.DISCONNECT_MESSAGE:
            sleep(0.01)

    def send_init(self):
        """

        """

        send_host = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')

        send_host.connect(self.SERVER_ADDR)
        send_host.send(self.add_padding(self.INIT_MESSAGE))
        self.wait(send_host)
        send_host.close()

    def send_indices_and_encrypt(self, index_a: int, index_b: int, swap: bool):
        """

        """

        send_host = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')

        send_host.connect(self.SERVER_ADDR)
        send_host.send(self.add_padding(self.ENCRYPT_EXECUTION_MESSAGE))
        send_host.send(self.add_padding(self.SENDING_INDICES_MESSAGE))
        send_host.send(self.add_padding(f"{index_a}"))
        send_host.send(self.add_padding(f"{index_b}"))
        self.wait(send_host)
        send_host.close()

        encryption_key_streams = self.get_key_streams()
        self.key_streams.extend(encryption_key_streams)
        self.write_as_MP_SPDZ_inputs(1, encryption_key_streams, int(swap))
        self.run_MP_SPDZ(compare_and_encrypt_mpc_script_path().stem, 1)

    def send_indices_and_reencrypt(self, index_a: int, index_b: int, swap: bool):
        """

        """

        send_host = self.client_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname='localhost')

        send_host.connect(self.SERVER_ADDR)
        send_host.send(self.add_padding(self.REENCRYPT_EXECUTION_MESSAGE))
        send_host.send(self.add_padding(self.SENDING_INDICES_MESSAGE))
        send_host.send(self.add_padding(f"{index_a}"))
        send_host.send(self.add_padding(f"{index_b}"))
        self.wait(send_host)
        send_host.close()

        decryption_key_streams = [self.key_streams[index_a], self.key_streams[index_b]]
        encryption_key_streams = self.get_key_streams()
        self.key_streams[index_a], self.key_streams[index_b] = encryption_key_streams
        self.write_as_MP_SPDZ_inputs(1, encryption_key_streams, int(swap), decryption_key_streams)
        self.run_MP_SPDZ(compare_and_reencrypt_mpc_script_path().stem, 1)

    def get_file_contents(self, file_path):
        """

        """

        with open(file_path, 'r') as file:
            contents = file.read()
            file.close()

        return contents

    def get_key_streams(self) -> list[list[str]]:
        """

        """

        key_streams = [get_key_streams(), get_key_streams()]
        return key_streams

    def twos_complement(self, hexadecimal_string: str):
        """  """
        value = int(hexadecimal_string, encoding_base())
        if (value & (1 << (block_size() - 1))) != 0:
            value = value - (1 << block_size())
        return value

    def write_encryption_keys(self):
        """

        """

        for i in range(database_size()):
            encryption_key_streams_path = encryption_keys_directory() / f"{i}.txt"
            with encryption_key_streams_path.open("w") as file:
                encryption_key_streams = self.key_streams[i]
                file.write(" ".join(encryption_key_streams))
                file.close()

    def write_as_MP_SPDZ_inputs(self, player_id: int, encryption_key_streams: list[list[str]], swap: int = None,
                                decryption_key_streams: list[list[str]] = None):
        """

        """

        with open(MP_SPDZ_input_path().parent / f"{MP_SPDZ_input_path()}-P{player_id}-0", 'w') as file:
            if swap is not None:
                file.write(f"{swap} \n")
            if decryption_key_streams:
                for i in range(len(decryption_key_streams)):
                    for block in range(len(decryption_key_streams[i])):
                        file.write(f"{int(decryption_key_streams[i][block], 16)} ")
                    file.write("\n")
            for i in range(len(encryption_key_streams)):
                for block in range(len(encryption_key_streams[i])):
                    file.write(f"{int(encryption_key_streams[i][block], 16)} ")
                file.write("\n")
            file.close()

    def run_MP_SPDZ(self, MP_SPDZ_script_name: str, player_id: int):
        """

        """

        chdir(MP_SPDZ_directory())

        client_MP_SPDZ_process = Popen([f"{MP_SPDZ_directory() / 'replicated-field-party.x'}",
                                        f"{MP_SPDZ_script_name}",
                                        "-p", f"{player_id}",
                                        "-IF", f"{MP_SPDZ_input_path()}",
                                        "-OF", f"{MP_SPDZ_output_path()}"]
                                       , stdout=PIPE, stderr=PIPE
                                       )

        client_output, client_error = client_MP_SPDZ_process.communicate()
        #print(client_error)
        client_MP_SPDZ_process.kill()

        chdir(working_directory())

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
            except Exception:
                print('[ERROR] incoming connection failed')

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
