""" Functionality of the server. """

# Imports.
from os import chdir
from re import findall
from pathlib import Path, PosixPath
from subprocess import Popen, PIPE
from json import loads
from random import shuffle

# Local getters imports.
from application.getters import (get_database_size as
                                 database_size)
from application.getters import (get_mp_spdz_protocol as
                                 mp_spdz_protocol)
from application.getters import (get_encoding_base as
                                 encoding_base)
from application.getters import (get_mp_spdz_directory as
                                 mp_spdz_directory)
from application.getters import (get_working_directory as
                                 working_directory)
from application.getters import (get_number_of_blocks as
                                 number_of_blocks)
from application.getters import (get_number_of_records as
                                 number_of_records)
from application.getters import (get_encrypted_records_directory as
                                 encrypted_records_directory)
from application.getters import (get_server_mp_spdz_input_path as
                                 mp_spdz_input_path)
from application.getters import (get_server_mp_spdz_output_path as
                                 mp_spdz_output_path)
from application.getters import (get_aes_128_ecb_with_circuit_mpc_script_path as
                                 aes_128_ecb_mpc_script_path)
from application.getters import (get_inverted_index_matrix_encryption_key_path as
                                 inverted_index_matrix_encryption_key_path)
from application.getters import (get_server_semantic_indexing_path as
                                 semantic_indexing_path)
from application.getters import (get_semantic_search_mpc_script_path as
                                 semantic_search_mpc_script_path)
from application.getters import (get_records_directory as
                                 records_directory)
from application.getters import (get_excluded_records as
                                 excluded_records)
from application.getters import (get_server_record_pointers_path as
                                 record_indexing_path)

# Server imports.
from application.Server.Utilities.key_stream_generator import get_key_stream
from application.Server.Utilities.Data_Generation.generate_passenger_number_records import run as generate_passenger_number_records
from application.Server.Utilities.semantic_indexing import run as create_semantic_indexing
from application.Server.Utilities.inverted_index_matrix import run as create_inverted_index_matrix
from application.Server.Utilities.record_encoder import encode_record
from application.Server.Utilities.inverted_index_matrix_encryptor import run as encrypt_inverted_index_matrix


class Utilities:
    """
        Implements the functionality of the server.
    """

    def __init__(self) -> None:
        self.is_semantic_search = None
        self.resume_from_previous_preprocessing = None
        self.indexing_finished = False
        self.record_pointers = None
        self.encrypted_record_pointers = None
        self.inverted_index_matrix_encryption_key = None

        return

    def resume(self) -> None:
        """
            Loads the stored data from previous pre-processing.

            Parameters:
                -

            Returns:
                :raises FileNotFoundError
                -
        """

        # Tries to load the encryption key used to encrypt the inverted index matrix.
        try:
            if not self.inverted_index_matrix_encryption_key and not self.is_semantic_search:
                with inverted_index_matrix_encryption_key_path().open('r') as f:
                    self.inverted_index_matrix_encryption_key = f.read()
                    f.close()

            if not self.encrypted_record_pointers:
                with record_indexing_path().open('r') as f:
                    self.encrypted_record_pointers = eval(f.read())
                    f.close()

            if self.is_semantic_search:
                self.indexing_finished = True
        except FileNotFoundError:
            pass

        return

    def generate_records(self) -> None:
        """
            Generates the PNR records.

            Parameters:
                -

            Returns:
                :raises
                -
        """

        generate_passenger_number_records(number_of_records())

        # Creates a list of pointers of the records and shuffles them.
        record_paths = [path for path in records_directory().glob('*') if
                        (path.name not in excluded_records()) and (path.suffix == '.json')]
        shuffle(record_paths)

        self.record_pointers = record_paths.copy()
        self.encrypted_record_pointers = record_paths

        return

    def semantic_indexing(self) -> None:
        """
            Creates a semantic indexing of the records.

            Parameters:
                -

            Returns:
                :raises
                -
        """

        create_semantic_indexing(self.record_pointers)

        return

    def create_inverted_index_matrix(self) -> None:
        """
            Creates an inverted index matrix of the records.

            Parameters:
                -

            Returns:
                :raises
                -
        """

        print('[INDEXING] Creating the inverted index matrix of the records.')
        create_inverted_index_matrix(self.record_pointers)

        return

    def setup_and_encode_records(self) -> None:
        """
            Encodes the records and stores them in the encrypted records directory. Additionally, fills the database
            with dummy items.

            Parameters:
                -

            Returns:
                :raises
                -
        """

        # Copies and encodes all records and dummy items into a new directory.
        for i in range(len(self.record_pointers)):
            record_path = self.record_pointers[i]
            # Encodes records.
            if record_path.suffix == ".json":
                encoded_record = encode_record(record_path)
            # Encodes dummy items.
            else:
                print('ranElse')
                with record_path.open("r") as f:
                    encoded_record = f.read()
                    f.close()

            # Stores the encoded copy.
            new_path = encrypted_records_directory() / f"{i}.txt"
            with new_path.open("w") as f:
                f.write(encoded_record)
                f.close()

            # Updates the local pointers.
            self.encrypted_record_pointers[i] = new_path

        # Fills the remainder of the database with dummy items.
        for i in range(number_of_records(), database_size()):
            dummy_item = ' '.join(get_key_stream()[0])

            # Writes the dummy item.
            file_path = encrypted_records_directory() / f'{i}.txt'
            with file_path.open('w') as f:
                f.write(dummy_item)
                f.close()

            # Updates database pointers with the dummy item.
            self.encrypted_record_pointers.append(file_path)

        return

    def write_encrypted_record_pointers(self) -> None:
        """
            Write the encrypted record pointers as a file.

            Parameters:
                -

            Returns:
                :raises
                -
        """

        with record_indexing_path().open('w') as f:
            f.write(f'{self.encrypted_record_pointers}')
            f.close()

        return

    def encrypt_records(self, index_a: int, index_b: int, mpc_script_name: str, host_address: str) -> None:
        """
            Obliviously encrypts the records with the client's keys.

            Parameters:
                - index_a (int) : Index to the pointer of a record.
                - index_b (int) : Index of the pointer of a record.
                - mpc_script_name (str) : Name of the .mpc script to be used.
                - host_address (str) : The hostname of the party to host the MP-SPDZ execution.

            Returns:
                :raises
                -
        """

        # Fetches the records.
        record_a, record_b = self.get_records(index_a, index_b)

        # Runs MP-SPDZ to obliviously encrypt the records with the client's keys then overwrites it.
        player_id = 0
        self.write_mp_spdz_input(player_id, [record_a, record_b])
        self.run_mp_spdz(player_id, mpc_script_name, host_address)
        record_path_a = encrypted_records_directory() / f"{index_a}.txt"
        record_path_b = encrypted_records_directory() / f"{index_b}.txt"
        self.encrypted_record_pointers[index_a], self.encrypted_record_pointers[index_b] = record_path_a, record_path_b
        self.write_mp_spdz_output_to_encrypted_records([record_path_a, record_path_b])

        return

    def get_records(self, index_a: int, index_b: int) -> tuple[list[str], list[str]]:
        """
            Obliviously encrypts the records with the client's keys.

            Parameters:
                - index_a (int) : Index to the pointer of a record.
                - index_b (int) : Index of the pointer of a record.

            Returns:
                :raises
                - record_a (bytes) : The encrypted record.
                - record_b (bytes) : The encrypted record.
        """

        # Fetches the records.
        record_path_a, record_path_b = self.encrypted_record_pointers[index_a], self.encrypted_record_pointers[index_b]

        # Reads the record.
        with record_path_a.open("r") as f:
            record_a = f.read().split(' ')
            f.close()

        # Reads the record.
        with record_path_b.open("r") as f:
            record_b = f.read().split(' ')
            f.close()

        return record_a, record_b

    @staticmethod
    def write_mp_spdz_input(player_id: int, records: list[list[str]]) -> None:
        """
            Writes records as correctly formatted inputs to be used with MP-SPDZ.

            Parameters:
                - player_id (int) : The player ID the records will be written to.
                - records (list[list[str]]) : The records is lists of blocks.

            Returns:
                :raises
                -
        """

        # Writes every block of the records as decimals to the server's MP-SPDZ input file.
        with open(mp_spdz_input_path().parent / f'{mp_spdz_input_path()}-P{player_id}-0', 'w') as f:
            for i in range(len(records)):
                for block in range(len(records[i])):
                    f.write(f'{int(records[i][block], encoding_base())} ')
                f.write('\n')
            f.close()

        return

    @staticmethod
    def run_mp_spdz(player_id: int, mpc_script_name: str, host_address: str) -> None:
        """
            Runs the server party and an additional empty party of the MP-SPDZ execution.

            Parameters:
                - player_id (int) : The player ID the records will be written to.
                - mpc_script_name (str) : Name of the .mpo script to be used.
                - host_address (str) : The hostname of the party to host the MP-SPDZ execution.

            Returns:
                :raises
                -
        """

        # Temporarily sets a new working directory
        chdir(mp_spdz_directory())

        # Runs the server party.
        server_mp_spdz_process = Popen([f"{mp_spdz_directory() / mp_spdz_protocol()}",
                                        f"{mpc_script_name}",
                                        "-p", f"{player_id}",
                                        '-h', f'{host_address}',
                                        "-IF", f"{mp_spdz_input_path()}",
                                        "-OF", f"{mp_spdz_output_path()}"],
                                       stdout=PIPE, stderr=PIPE
                                       )

        # Blocks until the process is finished and captures the standard out and standard error of the processes.
        server_output, server_error = server_mp_spdz_process.communicate()

        # Terminates the processes.
        server_mp_spdz_process.kill()

        # Changes back to the original working directory.
        chdir(working_directory())

        return

    @staticmethod
    def write_mp_spdz_output_to_encrypted_records(record_paths: list[Path]) -> None:
        """
            Takes the output of the MP-SPDZ execution and writes it as an encrypted record to the encrypted records'
            directory.

            Parameters:
                - record_paths (list[Path]) : The paths of the records.

            Returns:
                :raises
                -
        """

        # Finds all the hexadecimal blocks in the server's output.
        with open(mp_spdz_output_path().parent / f"{mp_spdz_output_path().name}-P0-0", "r") as f:
            hexadecimals_pattern = r"0x([a-fA-F0-9]+)"
            ciphertexts = findall(hexadecimals_pattern, f.read())
            f.close()

        # Writes the new records back to the encrypted records' directory.
        for i in range(len(record_paths)):
            with open(encrypted_records_directory() / record_paths[i], "w") as f:
                f.write(' '.join(ciphertexts[i * number_of_blocks(): (i + 1) * number_of_blocks()]))
                f.close()

        return

    def encrypt_inverted_index_matrix(self) -> None:
        """
            Encrypts all the keys of the inverted index matrix with the server's encryption key.

            Parameters:
                -

            Returns:
                :raises
                -
        """

        # Encrypts the inverted index matrix.
        encryption_key = encrypt_inverted_index_matrix()

        # Updates object variables.
        self.inverted_index_matrix_encryption_key = encryption_key
        self.write_indexing_encryption_key()

        return

    def write_indexing_encryption_key(self) -> None:
        """
            Writes the inverted index matrix encryption key to a file in the server's indexing directory.
            Parameters:
                -

            Returns:
                :raises
                -
        """

        # Writes the encryption key.
        with inverted_index_matrix_encryption_key_path().open("w") as f:
            f.write(self.inverted_index_matrix_encryption_key)
            f.close()

        return

    def semantic_search(self, host_address: str) -> None:
        """
            Obliviously compares the search query embedding with the semantic indexing, and returns the result to the
            client.

            Parameters:
                - host_address (str) : The hostname of the party to host the MP-SPDZ execution.
            Returns:
                :raises
                -
        """

        with semantic_indexing_path().open('r') as f:
            semantic_indexing = loads(f.read())
            f.close()

        player_id = 1
        for index in semantic_indexing.keys():
            self.write_embeddings_mp_spdz_input(player_id, semantic_indexing, index)
            self.run_mp_spdz(player_id, semantic_search_mpc_script_path().stem, host_address)

        return

    @staticmethod
    def write_embeddings_mp_spdz_input(player_id: int, semantic_indexing: dict[str, list[int]], index: str) -> None:
        """
            Writes an embedding vectory to the MP-SPDZ input file.

            Parameters:
                - player_id (int) : The player ID the key streams will be written to.
                - semantic_indexing (dict[str, list[int]]) : The embedding indexing of the records.
                - index (str) : Index of the record.
            Returns:
                :raises
                -
        """

        # Writes each record indices and value of the vector embeddings.
        with open(mp_spdz_input_path().parent / f'{mp_spdz_input_path()}-P{player_id}-0', 'w') as f:
            f.write(f'{index} ')
            for value in semantic_indexing[index]:
                f.write(f'{value} ')
            f.close()

        return

    def encrypt_query(self, host_address: str) -> None:
        """
            Obliviously encrypts the client's search query with the server's inverted index matrix encryption key.

            Parameters:
                - host_address (str) : The hostname of the party to host the MP-SPDZ execution.

            Returns:
                :raises
                -
        """

        # Runs MP-SPDZ to obliviously encrypt the client's search query.
        player_id = 1
        self.write_mp_spdz_input(player_id, [[self.inverted_index_matrix_encryption_key]])
        mpc_script_name = aes_128_ecb_mpc_script_path().stem
        self.run_mp_spdz(player_id, mpc_script_name, host_address)

        return
