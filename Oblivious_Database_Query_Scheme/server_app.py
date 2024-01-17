""" Runs the oblivious data query scheme """

from subprocess import run
from os import chdir

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

from Server.server import Communicator as Server


def clean_up_files():
    """

    """
    from Oblivious_Database_Query_Scheme.getters import get_excluded_PNR_records as excluded_PNR_records
    from Oblivious_Database_Query_Scheme.getters import get_client_indexing_directory as client_indexing_directory
    file_paths = [path for path in client_indexing_directory().glob('*')]
    for file_path in file_paths:
        file_path.unlink()

    from Oblivious_Database_Query_Scheme.getters import get_encrypted_PNR_records_directory as encrypted_PNR_records_directory
    file_paths = [path for path in encrypted_PNR_records_directory().glob('*')]
    for file_path in file_paths:
        file_path.unlink()

    from Oblivious_Database_Query_Scheme.getters import get_records_encryption_key_streams_directory as records_encryption_key_streams_directory
    file_paths = [path for path in records_encryption_key_streams_directory().glob('*')]
    for file_path in file_paths:
        file_path.unlink()

    from Oblivious_Database_Query_Scheme.getters import get_retrieved_records_directory as retrieved_records_directory
    file_paths = [path for path in retrieved_records_directory().glob('*')]
    for file_path in file_paths:
        file_path.unlink()

    from Oblivious_Database_Query_Scheme.getters import get_PNR_records_directory as PNR_records_directory
    file_paths = [path for path in PNR_records_directory().glob('*') if (path.name not in excluded_PNR_records())]
    for file_path in file_paths:
        file_path.unlink()

    from Oblivious_Database_Query_Scheme.getters import get_server_indexing_files_directory as server_indexing_files_directory
    file_paths = [path for path in server_indexing_files_directory().glob('*')]
    for file_path in file_paths:
        file_path.unlink()


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


if __name__ == '__main__':
    # Sets the working directory and validates it and MP-SPDZ's path
    working_directory_validation()
    MP_SPDZ_directory_validation()

    # Moves and compiles the MP-SDPZ scripts
    #setup_MPC_scripts()

    server = Server()
    server.wait_for_client()

    if not server.resume_from_previous:
        clean_up_files()

        # Initializes the database with PNR records
        server.create_database()

        # Creates an inverted index matrix of the database
        server.create_indexing()

        # Ephemeral encryption of the indexing
        server.encrypt_indexing()
        server.send_encrypted_indexing()

        server.wait_for_preprocessing()

    # Searching and file retrieval
    while server.client_online:
        server.wait_for_client_shutdown()

    server.kill()
