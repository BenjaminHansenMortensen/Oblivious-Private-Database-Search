""" Setup for the application. """

# Imports.
from os import chdir
from subprocess import run
from sentence_transformers import SentenceTransformer
from warnings import simplefilter

# Local getters imports.
from application.getters import working_directory_validation, mp_spdz_directory_validation
from application.getters import (get_mp_spdz_directory as
                                                       mp_spdz_directory)
from application.getters import (get_working_directory as
                                                       working_directory)
from application.getters import (get_mp_spdz_compile_path as
                                                       mp_spdz_compile_path)
from application.getters import (get_sort_and_encrypt_with_circuit_mpc_script_path as
                                                       sort_and_encrypt_with_circuit_mpc_script_path)
from application.getters import (get_sort_and_reencrypt_with_circuit_mpc_script_path as
                                                       sort_and_reencrypt_with_circuit_mpc_script_path)
from application.getters import (get_sort_and_encrypt_circuit_path as
                                                       sort_and_encrypt_circuit_path)
from application.getters import (get_sort_and_reencrypt_circuit_path as
                                                       sort_and_reencrypt_circuit_path)
from application.getters import (get_aes_128_ecb_with_circuit_mpc_script_path as
                                                       aes_128_ecb_with_circuit_mpc_script_path)
from application.getters import (get_mp_spdz_scripts_directory as
                                                       mp_spdz_scripts_directory)
from application.getters import (get_mp_spdz_circuits_directory as
                                                       mp_spdz_circuits_directory)
from application.getters import (get_encrypted_records_directory as
                                                       encrypted_pnr_records_directory)
from application.getters import (get_server_indexing_directory as
                                                       server_indexing_files_directory)
from application.getters import (get_server_encrypted_inverted_index_matrix_directory as
                                                       server_encrypted_inverted_index_matrix_directory)
from application.getters import (get_server_encryption_keys_directory as
                                                       server_encryption_keys_directory)
from application.getters import (get_server_mp_spdz_input_directory as
                                                       server_mp_spdz_input_directory)
from application.getters import (get_server_mp_spdz_output_directory as
                                                       server_mp_spdz_output_directory)
from application.getters import (get_records_directory as
                                                       records_directory)
from application.getters import (get_client_indexing_directory as
                                                       client_indexing_directory)
from application.getters import (get_client_encrypted_inverted_index_matrix_directory as
                                                       client_encrypted_inverted_index_matrix_directory)
from application.getters import (get_client_mp_spdz_input_directory as
                                                       client_mp_spdz_input_directory)
from application.getters import (get_client_mp_spdz_output_directory as
                                                       client_mp_spdz_output_directory)
from application.getters import (get_records_encryption_key_streams_directory as
                                                       records_encryption_key_streams_directory)
from application.getters import (get_retrieved_records_directory as
                                                       retrieved_records_directory)
from application.getters import (get_semantic_search_mpc_script_path as
                                                       semantic_search_mpc_script_path)
from application.getters import (get_embedding_model as
                                                       embedding_model)
                                                       
# Warning filtering.
simplefilter('ignore', UserWarning)


def create_necessary_directories() -> None:
    """
        Creates the necessary additional folders within this folder and sub-folders.

        Parameters:
            -

        Returns:
            :raises
            -
    """

    encrypted_pnr_records_directory().mkdir(exist_ok=True)
    server_indexing_files_directory().mkdir(exist_ok=True)
    server_encrypted_inverted_index_matrix_directory().mkdir(exist_ok=True)
    server_mp_spdz_input_directory().mkdir(exist_ok=True)
    server_mp_spdz_output_directory().mkdir(exist_ok=True)
    server_encryption_keys_directory().mkdir(exist_ok=True)
    records_directory().mkdir(exist_ok=True)
    client_indexing_directory().mkdir(exist_ok=True)
    client_encrypted_inverted_index_matrix_directory().mkdir(exist_ok=True)
    client_mp_spdz_input_directory().mkdir(exist_ok=True)
    client_mp_spdz_output_directory().mkdir(exist_ok=True)
    records_encryption_key_streams_directory().mkdir(exist_ok=True)
    retrieved_records_directory().mkdir(exist_ok=True)


def setup_mpc_scripts_and_circuits() -> None:
    """
        Moves the necessary .mpc scripts and the circuits they use over to the MP-SPDZ directory, then compiles the
        scripts.

        Parameters:
            -

        Returns:
            :raises
            -
    """

    chdir(mp_spdz_directory())

    # Moves and compiles the .mpc scripts.
    run(['cp', f'{aes_128_ecb_with_circuit_mpc_script_path()}',
               f'{mp_spdz_scripts_directory() / aes_128_ecb_with_circuit_mpc_script_path().name}'])
    run([f'{mp_spdz_compile_path()}', f'{aes_128_ecb_with_circuit_mpc_script_path().name}', '-B', '128'])
    run(['cp', f'{semantic_search_mpc_script_path()}',
               f'{mp_spdz_scripts_directory() / semantic_search_mpc_script_path().name}'])
    run([f'{mp_spdz_compile_path()}', f'{semantic_search_mpc_script_path().name}', '-B', '32'])

    chdir(working_directory())


def main() -> None:
    """

    """

    # Sets the working directory and validates it together with the MP-SPDZ's path.
    try:
        working_directory_validation()
        mp_spdz_directory_validation()
    except Exception as e:
        raise NotADirectoryError('Please verify the "working_directory" and "MP_SPDZ_directory" paths in getters.py')

    # Moves and compiles the MP-SPDZ scripts.
    setup_mpc_scripts_and_circuits()

    # Makes the required directories.
    create_necessary_directories()

    # Downloads the model.
    SentenceTransformer(embedding_model())

    return
