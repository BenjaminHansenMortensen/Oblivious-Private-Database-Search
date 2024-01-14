""" """

from os import chdir
from pathlib import Path
from re import findall
from subprocess import Popen, PIPE

from Oblivious_Database_Query_Scheme.getters import get_MP_SPDZ_directory as MP_SPDZ_directory
from Oblivious_Database_Query_Scheme.getters import get_working_directory as working_directory
from Oblivious_Database_Query_Scheme.getters import get_number_of_blocks as number_of_blocks
from Oblivious_Database_Query_Scheme.getters import get_database_size as database_size
from Oblivious_Database_Query_Scheme.getters import get_encrypted_PNR_records_directory as encrypted_PNR_records_directory
from Oblivious_Database_Query_Scheme.getters import get_server_MP_SPDZ_input_path as MP_SPDZ_input_path
from Oblivious_Database_Query_Scheme.getters import get_server_MP_SPDZ_output_path as MP_SPDZ_output_path
from Oblivious_Database_Query_Scheme.getters import get_aes_128_mpc_script_path as aes_128_mpc_script_path
from Oblivious_Database_Query_Scheme.getters import get_indexing_encryption_key_path as indexing_encryption_key_path

from Server.Data_Generation.generatePNR_Data import run as generate_PNR_records
from Server.Indexing.inverted_index_matrix import run as inverted_index_matrix
from Server.Encoding.file_encoder import encode_file
from Server.Indexing.indexing_encryptor import run as encrypt_indexing


class Utilities:
    """

    """

    def __init__(self):
        self.records_indexing = None
        self.indexing_encryption_key = None

    def create_database(self):
        """

        """

        generate_PNR_records(database_size())

    def create_indexing(self):
        """

        """

        self.records_indexing = inverted_index_matrix()

    def database_preprocessing(self):
        """

        """

        for i in range(len(self.records_indexing)):
            record_path = self.records_indexing[i]
            encoded_file = ' '.join(encode_file(record_path))

            record_copy_path = encrypted_PNR_records_directory() / f"{i}.txt"
            self.records_indexing[i] = record_copy_path
            with record_copy_path.open("w") as file:
                file.write(encoded_file)
                file.close()

    def retrieve_and_encrypt_files(self, index_a: int, index_b: int, MP_SPDZ_script_name: str):
        """

        """

        record_path_a, record_path_b = self.records_indexing[index_a], self.records_indexing[index_b]
        record_a, record_b = self.get_records(record_path_a), self.get_records(record_path_b)

        player_id = 0
        self.write_as_MP_SPDZ_inputs(player_id, [record_a, record_b])
        self.run_MP_SPDZ(player_id, MP_SPDZ_script_name)
        record_path_a = encrypted_PNR_records_directory() / f"{index_a}.txt"
        record_path_b = encrypted_PNR_records_directory() / f"{index_b}.txt"
        self.records_indexing[index_a], self.records_indexing[index_b] = record_path_a, record_path_b
        self.write_MP_SDPZ_output_to_encrypted_database([record_path_a, record_path_b])

    def get_records(self, record_path: Path) -> list[str]:
        """

        """

        with record_path.open("r") as file:
            encoded_record_a = file.read()
            file.close()

        return encoded_record_a.split(" ")

    def write_as_MP_SPDZ_inputs(self, player_id: int, records: list[list[str]]):
        with open(MP_SPDZ_input_path().parent / f"{MP_SPDZ_input_path()}-P{player_id}-0", 'w') as file:
            for i in range(len(records)):
                for block in range(len(records[i])):
                    file.write(f"{int(records[i][block], 16)} ")
                file.write("\n")
            file.close()

    def run_MP_SPDZ(self, player_id: int, MP_SPDZ_script_name: str):
        chdir(MP_SPDZ_directory())

        server_MP_SPDZ_process = Popen([f"{MP_SPDZ_directory() / 'replicated-field-party.x'}",
                                        f"{MP_SPDZ_script_name}",
                                        "-p", f"{player_id}",
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

        server_MP_SPDZ_process.kill()
        empty_party_MP_SPDZ_process.kill()

        chdir(working_directory())

    def write_MP_SDPZ_output_to_encrypted_database(self, file_names: list[Path]):
        """   """

        with open(MP_SPDZ_output_path().parent / f"{MP_SPDZ_output_path().name}-P0-0", "r") as file:
            hexadecimals_pattern = r"0x([a-fA-F0-9]+)"
            ciphertexts = findall(hexadecimals_pattern, file.read())
            file.close()

        for i in range(len(file_names)):
            with open(encrypted_PNR_records_directory() / file_names[i], "w") as file:
                file.write(' '.join(ciphertexts[i * number_of_blocks(): (i + 1) * number_of_blocks()]))
                file.close()

    def encrypt_indexing(self):
        """

        """

        encryption_key = encrypt_indexing()
        self.indexing_encryption_key = encryption_key
        self.write_indexing_encryption_key()

    def write_indexing_encryption_key(self):
        """

        """

        with indexing_encryption_key_path().open("w") as file:
            file.write(self.indexing_encryption_key)
            file.close()

    def encrypt_query(self):
        """

        """

        player_id = 1
        self.write_as_MP_SPDZ_inputs(player_id, [[self.get_indexing_encryption_key()]])
        MP_SPDZ_script_name = aes_128_mpc_script_path().stem
        self.run_MP_SPDZ(player_id, MP_SPDZ_script_name)

    def get_indexing_encryption_key(self) -> str:
        """

        """

        if not self.indexing_encryption_key:
            with indexing_encryption_key_path().open("r") as file:
                self.indexing_encryption_key = file.read()
                file.close()

        return self.indexing_encryption_key