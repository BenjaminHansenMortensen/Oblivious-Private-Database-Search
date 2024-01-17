""" """

# Imports
from os import chdir
from subprocess import run, PIPE

from Oblivious_Database_Query_Scheme.getters import working_directory_validation, MP_SPDZ_directory_validation

from Oblivious_Database_Query_Scheme.getters import get_MP_SPDZ_directory as MP_SPDZ_directory
from Oblivious_Database_Query_Scheme.getters import get_working_directory as working_directory
from Oblivious_Database_Query_Scheme.getters import get_MP_SDPZ_compile_path as MP_SPDZ_compile_path
from Oblivious_Database_Query_Scheme.getters import get_compare_and_encrypt_mpc_script_path as compare_and_encrypt_mpc_script_path
from Oblivious_Database_Query_Scheme.getters import get_compare_and_reencrypt_mpc_script_path as compare_and_reencrypt_mpc_script_path
from Oblivious_Database_Query_Scheme.getters import get_aes_128_mpc_script_path as aes_128_mpc_script_path
from Oblivious_Database_Query_Scheme.getters import get_MP_SPDZ_scripts_directory as MP_SDPZ_scripts_directory
from Oblivious_Database_Query_Scheme.getters import get_if_else_circuit_path as if_else_circuit_path
from Oblivious_Database_Query_Scheme.getters import get_MP_SPDZ_circuits_directory as MP_SPDZ_circuits_directory
from Oblivious_Database_Query_Scheme.getters import get_encrypted_PNR_records_directory as encrypted_PNR_records_directory
from Oblivious_Database_Query_Scheme.getters import get_server_indexing_files_directory as server_indexing_files_directory
from Oblivious_Database_Query_Scheme.getters import get_server_encryption_keys_directory as server_encryption_keys_directory
from Oblivious_Database_Query_Scheme.getters import get_server_MP_SPDZ_input_directory as server_MP_SPDZ_input_directory
from Oblivious_Database_Query_Scheme.getters import get_server_MP_SPDZ_output_directory as server_MP_SPDZ_output_directory
from Oblivious_Database_Query_Scheme.getters import get_server_networking_directory as server_networking_directory
from Oblivious_Database_Query_Scheme.getters import get_PNR_records_directory as PNR_records_directory
from Oblivious_Database_Query_Scheme.getters import get_client_indexing_directory as client_indexing_directory
from Oblivious_Database_Query_Scheme.getters import get_client_MP_SPDZ_input_directory as client_MP_SPDZ_input_directory
from Oblivious_Database_Query_Scheme.getters import get_client_MP_SPDZ_output_directory as client_MP_SPDZ_output_directory
from Oblivious_Database_Query_Scheme.getters import get_client_networking_directory as client_networking_directory
from Oblivious_Database_Query_Scheme.getters import get_records_encryption_key_streams_directory as records_encryption_key_streams_directory
from Oblivious_Database_Query_Scheme.getters import get_retrieved_records_directory as retrieved_records_directory


def create_necessary_directories():
    """

    """

    encrypted_PNR_records_directory().mkdir(exist_ok=True)
    server_indexing_files_directory().mkdir(exist_ok=True)
    server_MP_SPDZ_input_directory().mkdir(exist_ok=True)
    server_MP_SPDZ_output_directory().mkdir(exist_ok=True)
    server_networking_directory().mkdir(exist_ok=True)
    server_encryption_keys_directory().mkdir(exist_ok=True)
    PNR_records_directory().mkdir(exist_ok=True)
    client_indexing_directory().mkdir(exist_ok=True)
    client_MP_SPDZ_input_directory().mkdir(exist_ok=True)
    client_MP_SPDZ_output_directory().mkdir(exist_ok=True)
    client_networking_directory().mkdir(exist_ok=True)
    records_encryption_key_streams_directory().mkdir(exist_ok=True)
    retrieved_records_directory().mkdir(exist_ok=True)


def setup_MPC_scripts():
    """

    """

    chdir(MP_SPDZ_directory())

    run(["cp", f"{if_else_circuit_path()}", f"{MP_SPDZ_circuits_directory() / if_else_circuit_path().name}"])

    run(["cp", f"{compare_and_encrypt_mpc_script_path()}", f"{MP_SDPZ_scripts_directory() / compare_and_encrypt_mpc_script_path().name}"])
    run([f"{MP_SPDZ_compile_path()}", f"{compare_and_encrypt_mpc_script_path().name}", "-F", "128"])
    run(["cp", f"{compare_and_reencrypt_mpc_script_path()}", f"{MP_SDPZ_scripts_directory() / compare_and_reencrypt_mpc_script_path().name}"])
    run([f"{MP_SPDZ_compile_path()}", f"{compare_and_reencrypt_mpc_script_path().name}", "-F", "128"])
    run(["cp", f"{aes_128_mpc_script_path()}", f"{MP_SDPZ_scripts_directory() / aes_128_mpc_script_path().name}"])
    run([f"{MP_SPDZ_compile_path()}", f"{aes_128_mpc_script_path().name}", "-F", "128"])

    chdir(working_directory())

def create_networking_keys_and_certificates():
    """

    """

    run(['openssl', 'req', '-x509', '-newkey', 'rsa:4096', '-keyout', f'{server_networking_directory() / "key.pem"}',
         '-out', f'{server_networking_directory() / "cert.pem"}', '-sha256', '-days', '30', '-nodes', '-subj',
         '/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=localhost'
         ], stdout=PIPE, stderr=PIPE)

    run(['openssl', 'req', '-x509', '-newkey', 'rsa:4096', '-keyout', f'{client_networking_directory() / "key.pem"}',
         '-out', f'{client_networking_directory() / "cert.pem"}', '-sha256', '-days', '30', '-nodes', '-subj',
         '/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=localhost'
         ], stdout=PIPE, stderr=PIPE)

if __name__ == '__main__':
    # Sets the working directory and validates it and MP-SPDZ's path
    try:
        working_directory_validation()
        MP_SPDZ_directory_validation()
    except NotADirectoryError:
        raise NotADirectoryError('Please verify the "working_directory" and "MP_SPDZ_directory paths" in getters.py')

    # Moves and compiles the MP-SDPZ scripts
    #setup_MPC_scripts()

    # Makes the required directories
    create_necessary_directories()

    # Creates required networking certificates and keys for TLS
    create_networking_keys_and_certificates()

