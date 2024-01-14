"""  """

from os import chdir
from subprocess import Popen, PIPE
from hashlib import shake_128
from re import search
from json import dump
from pathlib import Path
from json import load

from Oblivious_Database_Query_Scheme.getters import get_number_of_bytes as number_of_bytes
from Oblivious_Database_Query_Scheme.getters import get_aes_128_mpc_script_path as aes_128_mpc_script_path
from Oblivious_Database_Query_Scheme.getters import get_client_MP_SPDZ_input_path as MP_SPDZ_input_path
from Oblivious_Database_Query_Scheme.getters import get_client_MP_SPDZ_output_path as MP_SPDZ_output_path
from Oblivious_Database_Query_Scheme.getters import get_MP_SPDZ_directory as MP_SPDZ_directory
from Oblivious_Database_Query_Scheme.getters import get_working_directory as working_directory
from Oblivious_Database_Query_Scheme.getters import get_records_encryption_key_streams_directory as encryption_keys_directory
from Oblivious_Database_Query_Scheme.getters import get_permutation_indexing_path as permutation_indexing_path
from Oblivious_Database_Query_Scheme.getters import get_compare_and_encrypt_mpc_script_path as compare_and_encrypt_mpc_script_path
from Oblivious_Database_Query_Scheme.getters import get_compare_and_reencrypt_mpc_script_path as compare_and_reencrypt_mpc_script_path
from Oblivious_Database_Query_Scheme.getters import get_client_encrypted_indexing_path as encrypted_indexing_path

from Client.Preprocessing.bitonic_sort import bitonic_sort
from Client.Preprocessing.key_stream_generator import get_key_streams


class Utilities:
    """

    """

    def __init__(self):
        self.encrypted_query = None
        self.permuted_index = None
        self.encrypted_indexing = None

    def database_preprocessing(self, client_communicator):
        """

        """

        self.permuted_index = bitonic_sort(client_communicator)
        self.write_indexing(self.permuted_index)

    def encrypt_files(self, swap: bool, index_a: int, index_b: int):
        """

        """

        player_id = 1
        encryption_key_streams = self.generate_key_streams()
        self.write_as_MP_SPDZ_inputs(player_id, encryption_key_streams, int(swap))
        self.run_MP_SPDZ(player_id, compare_and_encrypt_mpc_script_path().stem)
        self.write_encryption_keys(encryption_key_streams, [index_a, index_b])

    def reencrypt_files(self, swap: bool, index_a: int, index_b: int):
        """

        """
        decryption_key_streams_a_path = encryption_keys_directory() / f"{index_a}.txt"
        decryption_key_streams_b_path = encryption_keys_directory() / f"{index_b}.txt"

        player_id = 1
        decryption_key_streams = [self.get_key_streams(decryption_key_streams_a_path),
                                  self.get_key_streams(decryption_key_streams_b_path)]
        encryption_key_streams = self.generate_key_streams()
        self.write_as_MP_SPDZ_inputs(player_id, encryption_key_streams, int(swap), decryption_key_streams)
        self.run_MP_SPDZ(player_id, compare_and_reencrypt_mpc_script_path().stem)
        self.write_encryption_keys(encryption_key_streams, [index_a, index_b])

    def get_key_streams(self, key_streams_path: Path):
        """

        """

        with key_streams_path.open("r") as file:
            key_streams = file.read().split(" ")

        return key_streams

    def generate_key_streams(self) -> list[list[str]]:
        """

        """

        key_streams = [get_key_streams(), get_key_streams()]
        return key_streams

    def write_indexing(self, indexing: dict):
        """

        """

        with permutation_indexing_path().open('w') as file:
            dump(indexing, file, indent=4)
            file.close()

    def write_encryption_keys(self, encryption_key_streams: list[list[str]], indices: list[int]):
        """

        """

        for i in range(len(encryption_key_streams)):
            index = indices[i]
            encryption_key_streams_path = encryption_keys_directory() / f"{index}.txt"
            with encryption_key_streams_path.open("w") as file:
                file.write(" ".join(encryption_key_streams[i]))
                file.close()

    def encrypt_query(self, search_query: str):
        """

        """

        player_id = 0
        query_digest = shake_128(search_query.encode('ASCII')).digest(number_of_bytes()).hex()
        self.write_as_MP_SPDZ_inputs(player_id, [[query_digest]])
        self.run_MP_SPDZ(player_id, aes_128_mpc_script_path().stem)
        self.encrypted_query = self.get_MP_SPDZ_output(player_id)

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

    def run_MP_SPDZ(self, player_id: int, MP_SPDZ_script_name: str):
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

        client_MP_SPDZ_process.kill()

        chdir(working_directory())

    def get_MP_SPDZ_output(self, player_id: int) -> str:
        """

        """

        with open(MP_SPDZ_output_path().parent / f"{MP_SPDZ_output_path()}-P{player_id}-0", 'r') as file:
            hexadecimals_pattern = r"0x([a-fA-F0-9]+)"
            encrypted_query = search(hexadecimals_pattern, file.read()).group()
            encrypted_query = f"{int(encrypted_query, 16):0{32}x}"

        return encrypted_query

    def get_permuted_index(self, index: str):
        """

        """

        if not self.permuted_index:
            with permutation_indexing_path().open("r") as file:
                self.permuted_index = load(file)
                file.close()

        return self.permuted_index[index]

    def get_pointers(self):
        """

        """

        if not self.encrypted_indexing:
            with encrypted_indexing_path().open("r") as file:
                self.encrypted_indexing = load(file)
                file.close()

        return self.encrypted_indexing[self.encrypted_query]
