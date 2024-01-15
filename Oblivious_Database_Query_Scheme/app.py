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

from Client.client import Communicator as Client

from Server.server import Communicator as Server


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
    client = Client()

    # Initializes the database with PNR records
    server.create_database()

    # Creates an inverted index matrix of the database
    server.create_indexing()

    # Ephemeral encryption of the indexing
    server.encrypt_indexing()
    server.send_encrypted_indexing()

    # Creates a new secret database
    client.send_database_preprocessing_message()

    # Searching with file retrieval
    while True:

        # Take search query from the client
        search_query = input("Search Query: ")
        if search_query == "exit":
            break

        # Encrypted the search query under the server's encryption key
        client.send_encrypt_query_message(search_query)

        # Searches and retrieves the records
        client.request_PNR_records()

    server.kill()
    client.kill()
