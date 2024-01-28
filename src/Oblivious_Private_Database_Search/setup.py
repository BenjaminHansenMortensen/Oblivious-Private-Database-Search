""" Setup for the application. """
import argparse
# Imports.
from os import chdir
from subprocess import run, PIPE
from argparse import ArgumentParser

# Local getters imports.
from Oblivious_Private_Database_Search.getters import working_directory_validation, mp_spdz_directory_validation
from Oblivious_Private_Database_Search.getters import (get_mp_spdz_directory as
                                                       mp_spdz_directory)
from Oblivious_Private_Database_Search.getters import (get_working_directory as
                                                       working_directory)
from Oblivious_Private_Database_Search.getters import (get_mp_spdz_compile_path as
                                                       mp_spdz_compile_path)
from Oblivious_Private_Database_Search.getters import (get_sort_and_encrypt_with_circuit_mpc_script_path as
                                                       sort_and_encrypt_with_circuit_mpc_script_path)
from Oblivious_Private_Database_Search.getters import (get_sort_and_reencrypt_with_circuit_mpc_script_path as
                                                       sort_and_reencrypt_with_circuit_mpc_script_path)
from Oblivious_Private_Database_Search.getters import (get_sort_and_encrypt_circuit_path as
                                                       sort_and_encrypt_circuit_path)
from Oblivious_Private_Database_Search.getters import (get_sort_and_reencrypt_circuit_path as
                                                       sort_and_reencrypt_circuit_path)
from Oblivious_Private_Database_Search.getters import (get_aes_128_with_circuit_mpc_script_path as
                                                       aes_128_ecb_with_circuit_mpc_script_path)
from Oblivious_Private_Database_Search.getters import (get_mp_spdz_scripts_directory as
                                                       mp_spdz_scripts_directory)
from Oblivious_Private_Database_Search.getters import (get_mp_spdz_circuits_directory as
                                                       mp_spdz_circuits_directory)
from Oblivious_Private_Database_Search.getters import (get_encrypted_records_directory as
                                                       encrypted_pnr_records_directory)
from Oblivious_Private_Database_Search.getters import (get_server_indexing_files_directory as
                                                       server_indexing_files_directory)
from Oblivious_Private_Database_Search.getters import (get_server_encrypted_inverted_index_matrix_directory as
                                                       server_encrypted_inverted_index_matrix_directory)
from Oblivious_Private_Database_Search.getters import (get_server_encryption_keys_directory as
                                                       server_encryption_keys_directory)
from Oblivious_Private_Database_Search.getters import (get_server_mp_spdz_input_directory as
                                                       server_mp_spdz_input_directory)
from Oblivious_Private_Database_Search.getters import (get_server_mp_spdz_output_directory as
                                                       server_mp_spdz_output_directory)
from Oblivious_Private_Database_Search.getters import (get_server_networking_directory as
                                                       server_networking_directory)
from Oblivious_Private_Database_Search.getters import (get_records_directory as
                                                       pnr_records_directory)
from Oblivious_Private_Database_Search.getters import (get_client_indexing_directory as
                                                       client_indexing_directory)
from Oblivious_Private_Database_Search.getters import (get_client_encrypted_inverted_index_matrix_directory as
                                                       client_encrypted_inverted_index_matrix_directory)
from Oblivious_Private_Database_Search.getters import (get_client_mp_spdz_input_directory as
                                                       client_mp_spdz_input_directory)
from Oblivious_Private_Database_Search.getters import (get_client_mp_spdz_output_directory as
                                                       client_mp_spdz_output_directory)
from Oblivious_Private_Database_Search.getters import (get_client_networking_directory as
                                                       client_networking_directory)
from Oblivious_Private_Database_Search.getters import (get_records_encryption_key_streams_directory as
                                                       records_encryption_key_streams_directory)
from Oblivious_Private_Database_Search.getters import (get_retrieved_records_directory as
                                                       retrieved_records_directory)
from Oblivious_Private_Database_Search.getters import (get_semantic_search_mpc_script_path as
                                                       semantic_search_mpc_script_path)


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
    server_networking_directory().mkdir(exist_ok=True)
    server_encryption_keys_directory().mkdir(exist_ok=True)
    pnr_records_directory().mkdir(exist_ok=True)
    client_indexing_directory().mkdir(exist_ok=True)
    client_encrypted_inverted_index_matrix_directory().mkdir(exist_ok=True)
    client_mp_spdz_input_directory().mkdir(exist_ok=True)
    client_mp_spdz_output_directory().mkdir(exist_ok=True)
    client_networking_directory().mkdir(exist_ok=True)
    records_encryption_key_streams_directory().mkdir(exist_ok=True)
    retrieved_records_directory().mkdir(exist_ok=True)


def setup_mpc_scripts_and_circuits(exclude_semantic_search: bool) -> None:
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

    # Moves the circuits.
    run(['cp', f'{sort_and_encrypt_circuit_path()}',
               f'{mp_spdz_circuits_directory() / sort_and_encrypt_circuit_path().name}'])
    run(['cp', f'{sort_and_reencrypt_circuit_path()}',
               f'{mp_spdz_circuits_directory() / sort_and_reencrypt_circuit_path().name}'])

    # Moves and compiles the .mpc scripts.
    run(['cp', f'{sort_and_encrypt_with_circuit_mpc_script_path()}',
               f'{mp_spdz_scripts_directory() / sort_and_encrypt_with_circuit_mpc_script_path().name}'])
    run([f'{mp_spdz_compile_path()}', f'{sort_and_encrypt_with_circuit_mpc_script_path().name}', '-B', '128'])
    run(['cp', f'{sort_and_reencrypt_with_circuit_mpc_script_path()}',
               f'{mp_spdz_scripts_directory() / sort_and_reencrypt_with_circuit_mpc_script_path().name}'])
    run([f'{mp_spdz_compile_path()}', f'{sort_and_reencrypt_with_circuit_mpc_script_path().name}', '-B', '128'])
    run(['cp', f'{aes_128_ecb_with_circuit_mpc_script_path()}',
               f'{mp_spdz_scripts_directory() / aes_128_ecb_with_circuit_mpc_script_path().name}'])
    run([f'{mp_spdz_compile_path()}', f'{aes_128_ecb_with_circuit_mpc_script_path().name}', '-B', '128'])
    if not exclude_semantic_search:
        run(['cp', f'{semantic_search_mpc_script_path()}',
                   f'{mp_spdz_scripts_directory() / semantic_search_mpc_script_path().name}'])
        run([f'{mp_spdz_compile_path()}', f'{semantic_search_mpc_script_path().name}', '-B', '32'])

    chdir(working_directory())


def create_necessary_networking_keys_and_certificates() -> None:
    """
        Creates the necessary private keys and self-signed certificates for using TLS over sockets. The keys and
        certificates expire in 30 days and needs to be renewed after. The certificates are signed to be valid for the
        'localhost' domain.

        Parameters:
            -

        Returns:
            :raises
            -
    """

    # Creates private key and self-signed certificate for the server.
    run(['openssl', 'req', '-x509', '-newkey', 'rsa:4096', '-keyout', f'{server_networking_directory() / "key.pem"}',
         '-out', f'{server_networking_directory() / "cert.pem"}', '-sha256', '-days', '30', '-nodes', '-subj',
         '/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=localhost'
         ], stdout=PIPE, stderr=PIPE)
    # Creates private key and self-signed certificate for the client.
    run(['openssl', 'req', '-x509', '-newkey', 'rsa:4096', '-keyout', f'{client_networking_directory() / "key.pem"}',
         '-out', f'{client_networking_directory() / "cert.pem"}', '-sha256', '-days', '30', '-nodes', '-subj',
         '/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=localhost'
         ], stdout=PIPE, stderr=PIPE)


def main() -> None:
    """

    """

    parser = ArgumentParser()

    parser.add_argument('-es', '--exclude_semantic_search', action='store_true',
                        help='Excludes setting up the folders and scripts required for semantic searching.')

    args = parser.parse_args()
    exclude_semantic_search = args.exclude_semantic_search

    # Sets the working directory and validates it together with the MP-SPDZ's path.
    try:
        working_directory_validation()
        mp_spdz_directory_validation()
    except NotADirectoryError:
        raise NotADirectoryError('Please verify the "working_directory" and "MP_SPDZ_directory" paths in getters.py')

    # Moves and compiles the MP-SPDZ scripts.
    setup_mpc_scripts_and_circuits(exclude_semantic_search)

    # Makes the required directories.
    create_necessary_directories()

    # Creates required networking certificates and keys for communication.
    create_necessary_networking_keys_and_certificates()

    return
