""" Functionality of the client. """

# Imports.
from os import chdir
from subprocess import Popen, PIPE
from hashlib import shake_128
from re import search
from json import dump, load
from pathlib import Path, PosixPath
from random import randint
from numpy import multiply
from sentence_transformers import SentenceTransformer
from warnings import simplefilter

# Local getters imports.
from  Oblivious_Private_Database_Search.getters import (get_database_size as
                                                       database_size)
from  Oblivious_Private_Database_Search.getters import (get_number_of_bytes as
                                                       number_of_bytes)
from  Oblivious_Private_Database_Search.getters import (get_aes_128_with_circuit_mpc_script_path as
                                                       aes_128_mpc_script_path)
from  Oblivious_Private_Database_Search.getters import (get_client_mp_spdz_input_path as
                                                       mp_spdz_input_path)
from  Oblivious_Private_Database_Search.getters import (get_client_mp_spdz_output_path as
                                                       mp_spdz_output_path)
from  Oblivious_Private_Database_Search.getters import (get_mp_spdz_directory as
                                                       mp_spdz_directory)
from  Oblivious_Private_Database_Search.getters import (get_working_directory as
                                                       working_directory)
from  Oblivious_Private_Database_Search.getters import (get_records_encryption_key_streams_directory as
                                                       encryption_keys_directory)
from  Oblivious_Private_Database_Search.getters import (get_permutation_indexing_path as
                                                       permutation_indexing_path)
from  Oblivious_Private_Database_Search.getters import (get_sort_and_encrypt_with_circuit_mpc_script_path as
                                                       sort_and_encrypt_with_circuit_mpc_script_path)
from  Oblivious_Private_Database_Search.getters import (get_sort_and_reencrypt_with_circuit_mpc_script_path as
                                                       sort_and_reencrypt_with_circuit_mpc_script_path)
from  Oblivious_Private_Database_Search.getters import (get_client_encrypted_inverted_index_matrix_directory as
                                                       encrypted_indexing_path)
from  Oblivious_Private_Database_Search.getters import (get_requested_indices_path as
                                                       requested_indices_path)
from  Oblivious_Private_Database_Search.getters import (get_number_of_blocks as
                                                       number_of_blocks)
from  Oblivious_Private_Database_Search.getters import (get_records_encryption_key_streams_directory as
                                                       encryption_key_streams_directory)
from  Oblivious_Private_Database_Search.getters import (get_semantic_search_mpc_script_path as
                                                       semantic_search_mpc_script_path)
from  Oblivious_Private_Database_Search.getters import (get_request_threshold as
                                                       request_threshold)
from  Oblivious_Private_Database_Search.getters import (get_client_number_of_dummy_items_path as
                                                       number_of_dummy_items_path)
from  Oblivious_Private_Database_Search.getters import (get_embedding_model as
                                                       embedding_model)
from  Oblivious_Private_Database_Search.getters import (get_float_to_integer_scalar as
                                                       float_to_integer_scalar)
from  Oblivious_Private_Database_Search.getters import (get_number_of_records as
                                                       number_of_records)

# Client imports.
from  Oblivious_Private_Database_Search.Client.Utilities.bitonic_sort import bitonic_sort
from  Oblivious_Private_Database_Search.Client.Utilities.key_stream_generator import get_key_streams, aes_128_ctr


# Warning filtering.
simplefilter('ignore', UserWarning)


class Utilities:
    """
        Implements the functionality of the client.
    """

    def __init__(self) -> None:
        self.is_semantic_search = False
        self.resume_from_previous_preprocessing = False
        self.query_embedding = None
        self.encrypted_query = None
        self.permuted_indices = None
        self.number_of_dummy_items = None
        self.dummy_item_indices = None
        self.requests_to_make = None
        self.requested_indices = set()
        self.indices_to_request = set()

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

        # Tries to load the permuted indices, encrypted inverted index matrix, requested indices and dummy item indices.
        try:
            if not self.number_of_dummy_items:
                with number_of_dummy_items_path().open('r') as f:
                    self.number_of_dummy_items = int(f.read())
                    f.close()

            if not self.permuted_indices:
                with permutation_indexing_path().open('r') as f:
                    self.permuted_indices = load(f)
                    f.close()

            if not self.requested_indices:
                with requested_indices_path().open('r') as f:
                    self.requested_indices = eval(f.read())
                    f.close()

            if not self.dummy_item_indices:
                self.dummy_item_indices = list(
                                               {str(i) for i in range(database_size() -
                                                self.number_of_dummy_items, database_size())
                                                } -
                                               self.requested_indices
                                               )
        except FileNotFoundError:
            pass

        return

    def records_preprocessing(self, client_communicator) -> None:
        """
            Obliviously encrypts and shuffles all records and dummy items according to the client's permutation and 
            encryption keys.
                        
            Parameters:
                - client_communicator (Communicator) : The client.

            Returns:
                :raises FileNotFoundError
                -
        """

        # Shuffles and encrypts the records and dummy items.
        self.permuted_indices = bitonic_sort(client_communicator)

        # Writes the permutation.
        self.write_permutation(self.permuted_indices)

        # Derives the indices of the dummy items.
        self.dummy_item_indices = list(
                                        {str(i) for i in range(database_size() -
                                         self.number_of_dummy_items, database_size())
                                         }
                                        )

        return

    def encrypt_records(self, swap: bool, index_a: int, index_b: int, host_address: str) -> None:
        """
            Obliviously encrypts the records with the client's keys.

            Parameters:
                - swap (bool) : Indicator for whether the records should be swapped or not to be sorted.
                - index_a (int) : Index to the pointer of a record.
                - index_b (int) : Index to the pointer of a record.

            Returns:
                :raises
                -
        """

        encryption_key_streams_a, encryption_key_a, nonce_a = get_key_streams()
        encryption_key_streams_b, encryption_key_b, nonce_b = get_key_streams()
        encryption_key_streams = [encryption_key_streams_a, encryption_key_streams_b]

        # Runs MP-SPDZ to obliviously encrypt the records with the client's keys.
        player_id = 1
        self.write_mp_spdz_inputs(player_id, encryption_key_streams, int(swap))
        self.run_mp_spdz(player_id, sort_and_encrypt_with_circuit_mpc_script_path().stem, host_address)
        self.write_encryption_key_streams([index_a, index_b], [encryption_key_a, encryption_key_b], [nonce_a, nonce_b])

        return

    def reencrypt_records(self, swap: bool, index_a: int, index_b: int, host_address: str) -> None:
        """
            Obliviously re-encrypts the records with the client's keys.

            Parameters:
                - swap (bool) : Indicator for whether the records should be swapped or not to be sorted.
                - index_a (int) : Index to the pointer of a record.
                - index_b (int) : Index to the pointer of a record.
                
            Returns:
                :raises
                -
        """

        # Paths to the decryption keys.
        decryption_key_streams_a_path = encryption_keys_directory() / f'{index_a}.txt'
        decryption_key_streams_b_path = encryption_keys_directory() / f'{index_b}.txt'

        decryption_key_streams_a = self.get_stored_key_streams(decryption_key_streams_a_path)
        decryption_key_streams_b = self.get_stored_key_streams(decryption_key_streams_b_path)
        encryption_key_streams_a, encryption_key_a, nonce_a = get_key_streams()
        encryption_key_streams_b, encryption_key_b, nonce_b = get_key_streams()
        encryption_key_streams = [encryption_key_streams_a, encryption_key_streams_b]
        decryption_key_streams = [decryption_key_streams_a, decryption_key_streams_b]

        # Runs MP-SPDZ to obliviously re-encrypt the records with the client's keys.
        player_id = 1
        self.write_mp_spdz_inputs(player_id, encryption_key_streams, int(swap), decryption_key_streams)
        self.run_mp_spdz(player_id, sort_and_reencrypt_with_circuit_mpc_script_path().stem, host_address)
        self.write_encryption_key_streams([index_a, index_b], [encryption_key_a, encryption_key_b], [nonce_a, nonce_b])

        return

    @staticmethod
    def get_stored_key_streams(key_streams_path: Path) -> list[str]:
        """
            Gets the key streams used ot encrypt a record.
            
            Parameters:
                - key_streams_path (Path) : 

            Returns:
                :raises
                - key_streams (list[str]) : Key streams corresponding to a record.
        """

        # Reads the key streams.
        with key_streams_path.open('r') as f:
            key, nonce = f.read().split(' ')

        # Reproduce the key stream from the key and nonce.
        zero_plaintext = bytearray(number_of_bytes() * number_of_blocks())
        key_streams = aes_128_ctr(bytes.fromhex(key), zero_plaintext, bytes.fromhex(nonce))

        return key_streams

    @staticmethod
    def write_permutation(permutation: dict) -> None:
        """
            Writes the permutation to a file in the client's indexing directory.
            
            Parameters:
                - permutation (dict) : Permutation used to shuffle the server's records.

            Returns:
                :raises
                -
        """

        # Reads the permutation.
        with permutation_indexing_path().open('w') as f:
            dump(permutation, f, indent=4)
            f.close()

        return

    @staticmethod
    def write_encryption_key_streams(indices: list[int], keys: list[str], nonces: list[str]) -> None:
        """
            Obliviously encrypts and shuffles all records and dummy items according to the client's permutation and 
            encryption keys.
            
            Parameters:
                - indices (list[int]) : The indices corresponding to the key streams.
                - keys (list[str]) : Encryption keys to produce the key streams.
                - nonces (list[str]) : Nonces used to produce the key streams.

            Returns:
                :raises
                -
        """

        # Writes the encryption key streams.
        for i in range(len(indices)):
            index = indices[i]
            key = keys[i]
            nonce = nonces[i]
            encryption_key_streams_path = encryption_keys_directory() / f'{index}.txt'
            with encryption_key_streams_path.open('w') as f:
                f.write(f'{key} {nonce}')
                f.close()
        return

    def embedd_search_query(self, search_query: str) -> None:
        """

        """

        # Text embedding model.
        model = SentenceTransformer(embedding_model())

        # Gets the embedding of the record. (Requires internet connection)
        query_embedding = model.encode(f'{search_query}')

        # Scaled embedding from float to integer.
        scaled_query_embedding = multiply(query_embedding, float_to_integer_scalar()).astype(int).tolist()
        self.query_embedding = scaled_query_embedding

        return

    def semantic_search(self, host_address: str) -> None:
        """

        """

        smallest_distance = None
        pointer = None

        player_id = 0
        self.write_embedding_mp_spdz_input(player_id)
        for _ in range(number_of_records()):
            self.run_mp_spdz(player_id, semantic_search_mpc_script_path().stem, host_address)
            distance, index = self.get_semantic_search_result(player_id)

            if smallest_distance is None:
                smallest_distance = distance
                pointer = index
            elif distance < smallest_distance:
                smallest_distance = distance
                pointer = index

        self.indices_to_request.add(pointer)

        return

    def write_embedding_mp_spdz_input(self, player_id: int) -> None:
        """

        """

        with open(mp_spdz_input_path().parent / f'{mp_spdz_input_path()}-P{player_id}-0', 'w') as f:
            for value in self.query_embedding:
                f.write(f'{value} ')
            f.close()

        return

    @staticmethod
    def get_semantic_search_result(player_id: int) -> tuple[str, str]:
        """

        """

        with open(mp_spdz_output_path().parent / f'{mp_spdz_output_path()}-P{player_id}-0', 'r') as f:
            distance, pointer = f.read().strip().split(' ')
            f.close()

        return distance, pointer

    def encrypt_search_query(self, search_query: str, host_address: str) -> None:
        """
            Obliviously encrypts the client's search query with the server's inverted index matrix encryption key.
            
            Parameters:
                - search_query (str) : Client's search query.

            Returns:
                :raises
                -
        """

        # Runs MP-SPDZ to obliviously encrypt the client's search query.
        player_id = 0
        query_digest = shake_128(search_query.encode('ASCII')).digest(number_of_bytes()).hex()
        self.write_mp_spdz_inputs(player_id, [[query_digest]])
        self.run_mp_spdz(player_id, aes_128_mpc_script_path().stem, host_address)
        self.encrypted_query = self.get_mp_spdz_output()

        return

    @staticmethod
    def write_mp_spdz_inputs(player_id: int, encryption_key_streams: list[list[str]], swap: int = None,
                             decryption_key_streams: list[list[str]] = None) -> None:
        """
            Obliviously encrypts the client's search query with the server's inverted index matrix encryption key.

            Parameters:
                - player_id (int) : The player ID the key streams will be written to.
                - encryption_key_streams (list[list[str]]) : The encryption key streams.
                - swap (bool) : Indicator for whether the records should be swapped or not to be sorted.
                - decryption_key_streams (list[list[str]]) : The decryption key streams.

            Returns:
                :raises
                -
        """

        # Writes the swap indicator, decryption key streams,and encryption key streams as the client's MP-SPDZ input.
        with open(mp_spdz_input_path().parent / f'{mp_spdz_input_path()}-P{player_id}-0', 'w') as f:
            if swap is not None:
                f.write(f'{swap} \n')
            if decryption_key_streams:
                for i in range(len(decryption_key_streams)):
                    for block in range(len(decryption_key_streams[i])):
                        f.write(f'{int(decryption_key_streams[i][block], 16)} ')
                    f.write('\n')
            for i in range(len(encryption_key_streams)):
                for block in range(len(encryption_key_streams[i])):
                    f.write(f'{int(encryption_key_streams[i][block], 16)} ')
                f.write('\n')
            f.close()

        return

    @staticmethod
    def run_mp_spdz(player_id: int, mpc_script_name: str, host_address: str) -> None:
        """
            Runs the client party of the MP-SPDZ execution.

            Parameters:
                - player_id (int) : The player ID the records will be written to.
                - mpc_script_name (str) : Name of the .mpo script to be used.

            Returns:
                :raises
                -
        """

        # Temporarily sets a new working directory
        chdir(mp_spdz_directory())

        # Runs the client party.
        client_mp_spdz_process = Popen([f'{mp_spdz_directory() / "replicated-field-party.x"}',
                                        f'{mpc_script_name}',
                                        '-p', f'{player_id}',
                                        '-h', f'{host_address}',
                                        '-IF', f'{mp_spdz_input_path()}',
                                        '-OF', f'{mp_spdz_output_path()}'],
                                       stdout=PIPE, stderr=PIPE
                                       )

        # Blocks until the process is finished and captures the standard out and standard error of the processes.
        client_output, client_error = client_mp_spdz_process.communicate()

        # Terminates the processes.
        client_mp_spdz_process.kill()

        # Changes back to the original working directory.
        chdir(working_directory())

        return

    @staticmethod
    def get_mp_spdz_output() -> str:
        """
            Takes the output of the MP-SPDZ execution.

            Parameters:
                -

            Returns:
                :raises
                - encrypted_query (str) : Encrypted search query under the server's encryption key.
        """

        # Finds the hexadecimal encrypted search query in the client's output.
        with open(mp_spdz_output_path().parent / f'{mp_spdz_output_path()}-P0-0', 'r') as f:
            hexadecimals_pattern = r'0x([a-fA-F0-9]+)'
            encrypted_query = search(hexadecimals_pattern, f.read()).group()
            encrypted_query = f'{int(encrypted_query, 16):0{32}x}'

        return encrypted_query

    def get_indices(self) -> set[str]:
        """
            Compares the encrypted search query with the keys of the encrypted inverted index matrix and returns the
            resulting indices which points to the corresponding records on the server.

            Parameters:
                -

            Returns:
                :raises
                - search_query_result (str) : Indices of the pointers of records.
        """

        if self.is_semantic_search:
            search_query_result = self.indices_to_request - self.requested_indices
            if self.indices_to_request.issubset(self.requested_indices):
                print('[NO RESULT] Semantic search yielded an already requested record.')

        else:
            encrypted_inverted_index_matrix_part_paths = [path for path in encrypted_indexing_path().glob('*')
                                                          if path.suffix == '.json']
            for encrypted_inverted_index_matrix_part_path in encrypted_inverted_index_matrix_part_paths:
                with encrypted_inverted_index_matrix_part_path.open('r') as f:
                    encrypted_inverted_index_matrix_part = load(f)
                    f.close()

                if self.encrypted_query in encrypted_inverted_index_matrix_part:
                    self.indices_to_request.update(encrypted_inverted_index_matrix_part[self.encrypted_query])

            # Compares the encrypted search query with the encrypted inverted index matrx keys.
            if len(self.indices_to_request) == 0:
                print('[NO RESULT] Search query yielded no results.')
                search_query_result = set()
            else:
                if self.indices_to_request.issubset(self.requested_indices):
                    print('[NO RESULT] Search query yielded already requested record/records.')
                    search_query_result = set()
                else:
                    search_query_result = self.indices_to_request - self.requested_indices

        self.indices_to_request = set()

        return search_query_result

    def get_random_dummy_item_index(self) -> int:
        """
            Gets a random index of a dummy item on the server.

            Parameters:
                -

            Returns:
                :raises
                - random_dummy_item_index (int) : Index of a dummy item on the server.
        """

        # Gets a random index of a dummy item.
        random_dummy_item_index = self.dummy_item_indices.pop(randint(0, len(self.dummy_item_indices) - 1))

        return random_dummy_item_index

    def get_number_of_requests_to_make(self) -> int:
        """
            Takes the output of the MP-SPDZ execution and writes it as an encrypted record to the encrypted records'
            directory.

            Parameters:
                -

            Returns:
                :raises
                - requests_to_make (int) : The number of requests to be made with a single query.
        """

        # Inspects the encrypted inverted index matrix to find number of requests to be made so that all search query 
        # results look the same to the server.
        if not self.requests_to_make and not self.is_semantic_search:

            largest_set_of_indices = 0
            encrypted_inverted_index_matrix_part_paths = [path for path in encrypted_indexing_path().glob('*')
                                                          if path.suffix == '.json']
            for encrypted_inverted_index_matrix_part_path in encrypted_inverted_index_matrix_part_paths:
                with encrypted_inverted_index_matrix_part_path.open('r') as f:
                    encrypted_inverted_index_matrix_part = load(f)
                    f.close()

                parts_largest_set_of_indices = max([len(indices)
                                                    for indices in encrypted_inverted_index_matrix_part.values()]
                                                   )

                if parts_largest_set_of_indices > largest_set_of_indices:
                    largest_set_of_indices = parts_largest_set_of_indices

            self.requests_to_make = largest_set_of_indices
        elif not self.requests_to_make and self.is_semantic_search:
            self.requests_to_make = request_threshold()

        return self.requests_to_make

    def write_requested_indices(self) -> None:
        """
            Writes the already requested server indices to a file.

            Parameters:
                - record_paths (list[Path]) : The paths of the records.

            Returns:
                :raises
                -
        """

        # Writes the requested indices.
        with requested_indices_path().open('w') as f:
            f.write(self.requested_indices.__str__())
            f.close()

        return

    @staticmethod
    def get_record_key_streams(index: str) -> list[str]:
        """
            Gets the corresponding key streams to an index.

            Parameters:
                - index (str) : Index to the pointer of the encryption key stream of the record.

            Returns:
                :raises
                - encryption_key_streams (list[str]) : Key streams to the encrypted record.
        """

        # Reads the encryption key streams.
        key_streams_path = encryption_key_streams_directory() / f'{index}.txt'
        with key_streams_path.open('r') as f:
            key, nonce = f.read().split(' ')
            f.close()

        zero_plaintext = bytearray(number_of_bytes() * number_of_blocks())
        encryption_key_streams = aes_128_ctr(bytes.fromhex(key), zero_plaintext, bytes.fromhex(nonce))

        return encryption_key_streams
