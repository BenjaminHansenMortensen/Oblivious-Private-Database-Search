""" Handling the communication with the client """

from time import sleep
from os import chdir
from pathlib import Path
from re import findall
from threading import Thread
from subprocess import Popen, PIPE
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, timeout
from ssl import SSLContext, PROTOCOL_TLS_CLIENT, PROTOCOL_TLS_SERVER
from Oblivious_Database_Query_Scheme.getters import get_working_directory as working_directory
from Oblivious_Database_Query_Scheme.getters import get_number_of_blocks as number_of_blocks
from Oblivious_Database_Query_Scheme.getters import get_block_size as block_size
from Oblivious_Database_Query_Scheme.getters import get_encoding_base as encoding_base
from Oblivious_Database_Query_Scheme.getters import get_MP_SPDZ_directory as MP_SPDZ_directory
from Oblivious_Database_Query_Scheme.getters import get_excluded_PNR_records as excluded_PNR_records
from Oblivious_Database_Query_Scheme.getters import get_server_MP_SPDZ_input_path as MP_SPDZ_input_path
from Oblivious_Database_Query_Scheme.getters import get_server_MP_SPDZ_output_path as MP_SPDZ_output_path
from Oblivious_Database_Query_Scheme.getters import get_encrypted_PNR_records_directory as encrypted_PNR_records_directory
from Oblivious_Database_Query_Scheme.getters import get_PNR_records_directory as PNR_records_directory
from Server.Encoding.file_encoder import encode_file


class Communicate:
    """
        Establishes a secure communication channel between the server and client.
        Allowing them to send and receive json files.
    """
    def __init__(self):
        self.HEADER = 1024
        self.LISTEN_PORT = 5005
        self.HOST = 'localhost'
        self.ADDR = (self.HOST, self.LISTEN_PORT)
        self.CLIENT_ADDR = ('localhost', 5500)
        self.FORMAT = 'utf-8'

        self.SENDING_JSON_MESSAGE = '<SENDING JSON>'
        self.INIT_MESSAGE = '<INIT>'
        self.ENCRYPT_EXECUTION_MESSAGE = '<ENCRYPT EXECUTION>'
        self.REENCRYPT_EXECUTION_MESSAGE = '<REENCRYPT EXECUTION>'
        self.SENDING_INDICES_MESSAGE = '<SENDING INDICES>'
        self.FILE_NAME_MESSAGE = '<FILE NAME>'
        self.FILE_CONTENTS_MESSAGE = '<FILE CONTENTS>'
        self.DISCONNECT_MESSAGE = '<DISCONNECT>'
        self.END_FILE_MESSAGE = '<END FILE>'

        self.records_indexing = None

        self.server_context = SSLContext(PROTOCOL_TLS_SERVER)
        self.server_context.load_cert_chain(certfile='Server/Networking/Keys/cert.pem', keyfile='Server/Networking/Keys/key.pem')
        self.client_context = SSLContext(PROTOCOL_TLS_CLIENT)
        self.client_context.load_verify_locations('Client/Networking/Keys/cert.pem')
        self.listen_host = self.server_context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_side=True)
        self.listen_host.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.listen_host.settimeout(0.2)

        self.close = False
        self.listen_thread = []
        self.run_thread = Thread(target=self.run)
        self.run_thread.start()

    def receive(self, connection, address):
        """

        """

        message = connection.recv(self.HEADER).decode(self.FORMAT).strip()
        print(f'[RECEIVED] {message} from {address}')
        if message == self.SENDING_JSON_MESSAGE:
            self.receive_json(connection, address)
        elif message == self.INIT_MESSAGE:
            self.init_encrypted_database(connection, address)
            connection.send(self.add_padding(self.DISCONNECT_MESSAGE))
        elif message == self.ENCRYPT_EXECUTION_MESSAGE:
            self.MP_SPDZ_execution(connection, address, "compare_and_encrypt")
        elif message == self.REENCRYPT_EXECUTION_MESSAGE:
            self.MP_SPDZ_execution(connection, address, "compare_and_reencrypt")

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

        send_host.connect(self.CLIENT_ADDR)
        send_host.send(self.add_padding(self.FILE_NAME_MESSAGE))
        send_host.send(self.add_padding(f'{file_name}'))
        send_host.send(self.add_padding(self.FILE_CONTENTS_MESSAGE))
        send_host.send(self.add_padding(f'{file_contents}'))
        send_host.send(self.add_padding(self.END_FILE_MESSAGE))
        send_host.send(self.add_padding(self.DISCONNECT_MESSAGE))
        send_host.close()

    def wait(self, connection):
        """

        """

        while (message := connection.recv(self.HEADER).decode(self.FORMAT).strip()) != self.DISCONNECT_MESSAGE:
            sleep(0.01)

    def get_file_contents(self, file_path):
        """

        """

        with open(file_path, 'r') as file:
            contents = file.read()
            file.close()

        return contents

    def init_encrypted_database(self, connection, address):
        """

        """

        self.records_indexing = sorted(
            [path for path in PNR_records_directory().glob('*') if path.name not in excluded_PNR_records()],
            key=lambda x: int(findall(r"\d+", string=x.name)[0]))

        for i in range(len(self.records_indexing)):
            record_path = self.records_indexing[i]
            encoded_file = ' '.join(encode_file(record_path))

            record_copy_path = encrypted_PNR_records_directory() / f"{i}.txt"
            self.records_indexing[i] = record_copy_path
            with record_copy_path.open("w") as file:
                file.write(encoded_file)
                file.close()

        connection.send(self.add_padding(self.DISCONNECT_MESSAGE))

    def MP_SPDZ_execution(self, connection, address, MP_SPDZ_script_name: str):
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
            # Get files
            record_path_a, record_path_b = self.records_indexing[index_a], self.records_indexing[index_b]
            record_a, record_b = self.get_records(record_path_a), self.get_records(record_path_b)
            self.write_as_MP_SPDZ_inputs([record_a, record_b])
            self.run_MP_SPDZ(MP_SPDZ_script_name)
            record_path_a, record_path_b = encrypted_PNR_records_directory() / f"{index_a}.txt", encrypted_PNR_records_directory() / f"{index_b}.txt"
            self.records_indexing[index_a], self.records_indexing[index_b] = record_path_a, record_path_b
            self.write_MP_SDPZ_output_to_encrypted_database([record_path_a, record_path_b])


    def twos_complement(self, hexadecimal_string: str):
        """  """
        value = int(hexadecimal_string, encoding_base())
        if (value & (1 << (block_size() - 1))) != 0:
            value = value - (1 << block_size())
        return value

    def write_as_MP_SPDZ_inputs(self, records: list[list[str]]):
        with open(MP_SPDZ_input_path().parent / f"{MP_SPDZ_input_path()}-P0-0", 'w') as file:
            for i in range(len(records)):
                for block in range(len(records[i])):
                    file.write(f"{self.twos_complement(records[i][block])} ")
                file.write("\n")
            file.close()

    def get_records(self, record_path: Path) -> list[str]:
        """

        """

        encoded_record_a = self.get_file_contents(record_path)
        return encoded_record_a.split(' ')

    def run_MP_SPDZ(self, MP_SPDZ_script_name: str):
        chdir(MP_SPDZ_directory())

        server_MP_SPDZ_process = Popen([f"{MP_SPDZ_directory() / 'replicated-field-party.x'}",
                                        f"{MP_SPDZ_script_name}",
                                        "-p", "0",
                                        "-IF", f"{MP_SPDZ_input_path()}",
                                        "-OF", f"{MP_SPDZ_output_path()}"]
                                       , stdout=PIPE, stderr=PIPE
                                       )
        empty_party_MP_SPDZ_process = Popen([f"{MP_SPDZ_directory() / 'replicated-field-party.x'}",
                                             f"{MP_SPDZ_script_name}",
                                             "-p", "2"]
                                            , stdout=PIPE, stderr=PIPE
                                            )

        server_output, server_error = server_MP_SPDZ_process.communicate()
        empty_party_output, empty_party_error = empty_party_MP_SPDZ_process.communicate()

        # server_MP_SPDZ_process.wait()
        # empty_party_MP_SPDZ_process.wait()

        server_MP_SPDZ_process.kill()
        empty_party_MP_SPDZ_process.kill()

        chdir(working_directory())

    def write_MP_SDPZ_output_to_encrypted_database(self, file_names: list[str]):
        """   """

        with open(MP_SPDZ_output_path().parent / f"{MP_SPDZ_output_path().name}-P0-0", "r") as file:
            hexadecimals_pattern = r"0x([a-fA-F0-9]+)"
            ciphertexts = findall(hexadecimals_pattern, file.read())
            file.close()

        for i in range(len(file_names)):
            with open(encrypted_PNR_records_directory() / file_names[i], "w") as file:
                file.write(' '.join(ciphertexts[i * number_of_blocks(): (i + 1) * number_of_blocks()]))
                file.close()

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
                #thread = Thread(target=self.receive, args=(conn, addr))
                #thread.start()
                #self.listen_thread.append(thread)
            except timeout:
                continue
            except Exception as e:
                print(f'[ERROR] incoming connection failed as {e}')

    def kill(self):
        """
            Closes the communication.

            Parameters:
                -

            Returns:

        """

        #for thread in self.listen_thread:
        #    thread.join()
        #self.listen_host.close()
        self.close = True
        self.run_thread.join()
        print(f'[CLOSED] {self.ADDR}')
