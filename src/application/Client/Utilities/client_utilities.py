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
from numpy import fromstring

# Local getters imports.
from application.getters import (get_mp_spdz_protocol as
                                                       mp_spdz_protocol)
from application.getters import (get_database_size as
                                                       database_size)
from application.getters import (get_number_of_bytes as
                                                       number_of_bytes)
from application.getters import (get_aes_128_ecb_with_circuit_mpc_script_path as
                                                       aes_128_ecb_mpc_script_path)
from application.getters import (get_client_mp_spdz_input_path as
                                                       mp_spdz_input_path)
from application.getters import (get_client_mp_spdz_output_path as
                                                       mp_spdz_output_path)
from application.getters import (get_mp_spdz_directory as
                                                       mp_spdz_directory)
from application.getters import (get_working_directory as
                                                       working_directory)
from application.getters import (get_records_encryption_key_streams_directory as
                                                       records_encryption_keys_directory)
from application.getters import (get_permutation_indexing_path as
                                                       permutation_indexing_path)
from application.getters import (get_client_encrypted_inverted_index_matrix_directory as
                                                       encrypted_inverted_index_matrix_directory)
from application.getters import (get_requested_indices_path as
                                                       requested_indices_path)
from application.getters import (get_number_of_blocks as
                                                       number_of_blocks)
from application.getters import (get_semantic_search_mpc_script_path as
                                                       semantic_search_mpc_script_path)
from application.getters import (get_semantic_search_request_threshold as
                                                       request_threshold)
from application.getters import (get_client_number_of_dummy_items_path as
                                                       number_of_dummy_items_path)
from application.getters import (get_embedding_model as
                                                       embedding_model)
from application.getters import (get_float_to_integer_scalar as
                                                       float_to_integer_scalar)
from application.getters import (get_number_of_records as
                                                       number_of_records)

# Client imports.
from application.Client.Utilities.bitonic_sort import bitonic_sort
from application.Client.Utilities.key_stream_generator import aes_128_ctr


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
                self.dummy_item_indices = list({str(i) for i in range(database_size() -
                                                self.number_of_dummy_items, database_size())} -
                                               self.requested_indices
                                               )
        except FileNotFoundError:
            pass

        return

    def records_preprocessing(self, client_communicator, connection) -> None:
        """
            Obliviously encrypts and shuffles all records and dummy items according to the client's permutation and 
            encryption keys.
                        
            Parameters:
                - client_communicator (Communicator) : The client.
                - connection (SSLSocket) : Connection with the server.

            Returns:
                :raises FileNotFoundError
                -
        """

        # Shuffles and encrypts the records and dummy items.
        self.permuted_indices = bitonic_sort(client_communicator, connection)

        # Writes the permutation.
        self.write_permutation(self.permuted_indices)

        # Derives the indices of the dummy items.
        self.dummy_item_indices = list({str(i) for i in range(database_size() -
                                        self.number_of_dummy_items, database_size())}
                                       )

        return

    @staticmethod
    def xor(bytes_a: bytes, bytes_b: bytes) -> bytes:
        """
            XORs two bytes objects.

            Parameters:
                - bytes_a (bytes) : Bytes object to be XORed.
                - bytes_b (bytes) : Bytes object to be XORed.

            Returns:
                :raises
                - bytes_a ^ bytes_b (bytes) : Byte objects XORed.

        """

        bytestring_a = fromstring(bytes_a, dtype='uint8', sep='', count=-1)
        bytestring_b = fromstring(bytes_b, dtype='uint8', sep='', count=-1)

        return (bytestring_a ^ bytestring_b).tobytes()

    @staticmethod
    def get_stored_encryption_key(index: int) -> bytes:
        """
            Gets the key streams used ot encrypt a record.
            
            Parameters:
                - index (int) : Index of the pointer to the record.

            Returns:
                :raises
                - key_stream (bytes) : Key streams corresponding to a record.
        """

        key_path = records_encryption_keys_directory() / f'{index}.txt'

        # Reads the key streams.
        with key_path.open('r') as f:
            key, nonce = f.read().split(' ')

        # Reproduce the key stream from the key and nonce.
        zero_plaintext = bytearray(number_of_bytes() * number_of_blocks())
        key_stream = aes_128_ctr(bytes.fromhex(key), zero_plaintext, bytes.fromhex(nonce))

        return key_stream

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
    def write_encryption_keys(indices: list[int], keys: list[bytes], nonces: list[bytes]) -> None:
        """
            Obliviously encrypts and shuffles all records and dummy items according to the client's permutation and 
            encryption keys.
            
            Parameters:
                - indices (list[int]) : The indices corresponding to the key streams.
                - keys (list[bytes]) : Encryption keys to produce the key streams.
                - nonces (list[bytes]) : Nonces used to produce the key streams.

            Returns:
                :raises
                -
        """

        # Writes the encryption key streams.
        for i in range(len(indices)):
            index = indices[i]
            key = keys[i].hex()
            nonce = nonces[i].hex()
            encryption_key_streams_path = records_encryption_keys_directory() / f'{index}.txt'
            with encryption_key_streams_path.open('w') as f:
                f.write(f'{key} {nonce}')
                f.close()

        return

    def get_search_query_embedding(self, search_query: str) -> None:
        """
            Gets the vector embedding of the user's search query.

            Parameters:
                - search_query (str) : The search query input from the user.

            Returns:
                :raises
                -
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
            Obliviously compares the search query embedding with the semantic indexing, and returns the result to the
            client.

            Parameters:
                - host_address (str) : The hostname of the party to host the MP-SPDZ execution.

            Returns:
                :raises
                -
        """

        # OBS INSECURE FOR DEMONSTRATIVE PURPOSES.
        # Compares the search query embedding to each record embedding one by one and sorts them by smallest distance.
        results = []
        player_id = 0
        self.write_embedding_mp_spdz_input(player_id)
        for _ in range(number_of_records()):
            self.run_mp_spdz(player_id, semantic_search_mpc_script_path().stem, host_address)
            results.append(self.get_semantic_search_result(player_id))

        # Updates local variable with the closes record indices.
        results.sort(key=lambda x: x[0])
        for i in range(request_threshold()):
            self.indices_to_request.add(results[i][1])

        return

    def write_embedding_mp_spdz_input(self, player_id: int) -> None:
        """
            Writes an embedding vectory to the MP-SPDZ input file.

            Parameters:
                - player_id (int) : The player ID the key streams will be written to.

            Returns:
                :raises
                -
        """

        # Writes each value of the vector embedding.
        with open(mp_spdz_input_path().parent / f'{mp_spdz_input_path()}-P{player_id}-0', 'w') as f:
            for value in self.query_embedding:
                f.write(f'{value} ')
            f.close()

        return

    @staticmethod
    def get_semantic_search_result(player_id: int) -> tuple[str, str]:
        """
            Gets the result of the oblivious comparison of the search query embedding and a record embedding from the
            MP-SPDZ output file.

            Parameters:
                - player_id (int) : The player ID the key streams will be written to.

            Returns:
                :raises
                -
        """

        with open(mp_spdz_output_path().parent / f'{mp_spdz_output_path()}-P{player_id}-0', 'r') as f:
            distance, index = f.read().strip().split(' ')
            f.close()

        return distance, index

    def encrypt_search_query(self, search_query: str, host_address: str) -> None:
        """
            Obliviously encrypts the client's search query with the server's inverted index matrix encryption key.
            
            Parameters:
                - search_query (str) : Client's search query.
                - host_address (str) : The hostname of the party to host the MP-SPDZ execution.

            Returns:
                :raises
                -
        """

        # Runs MP-SPDZ to obliviously encrypt the client's search query.
        player_id = 0
        query_digest = shake_128(search_query.encode('ASCII')).digest(number_of_bytes()).hex()
        self.write_mp_spdz_inputs(player_id, query_digest)
        self.run_mp_spdz(player_id, aes_128_ecb_mpc_script_path().stem, host_address)
        self.encrypted_query = self.get_mp_spdz_output()

        return

    @staticmethod
    def write_mp_spdz_inputs(player_id: int, query_digest: str) -> None:
        """
            Obliviously encrypts the client's search query with the server's inverted index matrix encryption key.

            Parameters:
                - player_id (int) : The player ID the key streams will be written to.
                - query_digest (str) : The digest of the search query.

            Returns:
                :raises
                -
        """

        # Writes the swap indicator, decryption key streams,and encryption key streams as the client's MP-SPDZ input.
        with open(mp_spdz_input_path().parent / f'{mp_spdz_input_path()}-P{player_id}-0', 'w') as f:
            f.write(f'{int(query_digest, 16)} ')
            f.close()

        return

    @staticmethod
    def run_mp_spdz(player_id: int, mpc_script_name: str, host_address: str) -> None:
        """
            Runs the client party of the MP-SPDZ execution.

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

        # Runs the client party.
        client_mp_spdz_process = Popen([f'{mp_spdz_directory() / mp_spdz_protocol()}',
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
                - search_query_result (str) : Indices of the pointers to records.
        """

        if self.is_semantic_search:
            # Returns the result from the semantic search.
            search_query_result = self.indices_to_request - self.requested_indices
            if self.indices_to_request.issubset(self.requested_indices):
                print('[NO RESULT] Semantic search yielded an already requested record.')
        else:
            # Gets the paths for all the parts of the encrypted inverted index matrix.
            encrypted_inverted_index_matrix_part_paths = [path for path in
                                                          encrypted_inverted_index_matrix_directory().glob('*')
                                                          if path.suffix == '.json']

            # Searches each part of the encrypted inverted index matrix.
            for encrypted_inverted_index_matrix_part_path in encrypted_inverted_index_matrix_part_paths:
                with encrypted_inverted_index_matrix_part_path.open('r') as f:
                    encrypted_inverted_index_matrix_part = load(f)
                    f.close()

                # Updates the results from the search of that part.
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
            # Gets the paths for all the parts of the encrypted inverted index matrix.
            encrypted_inverted_index_matrix_part_paths = [path for path in
                                                          encrypted_inverted_index_matrix_directory().glob('*')
                                                          if path.suffix == '.json']

            # Finds the largest set of indices in each part and keeps the largest.
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
                -

            Returns:
                :raises
                -
        """

        # Writes the requested indices.
        with requested_indices_path().open('w') as f:
            f.write(self.requested_indices.__str__())
            f.close()

        return
