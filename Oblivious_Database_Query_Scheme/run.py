""" Runs the oblivious data query scheme """

from subprocess import run
from Oblivious_Database_Query_Scheme.getters import working_directory_validation, MP_SPDZ_directory_validation
from Oblivious_Database_Query_Scheme.getters import get_MP_SDPZ_compile_path as MP_SPDZ_compile_path
from Oblivious_Database_Query_Scheme.getters import get_compare_and_encrypt_mpc_script_path as compare_and_encrypt_mpc_script_path
from Oblivious_Database_Query_Scheme.getters import get_compare_and_reencrypt_mpc_script_path as compare_and_reencrypt_mpc_script_path
from Oblivious_Database_Query_Scheme.getters import get_MP_SPDZ_scripts_directory as MP_SDPZ_scripts_directory

from Client.Networking.client import Communicate as Client

from Server.Networking.server import Communicate as Server
from Server.Indexing.inverted_index_matrix import run as create_indexing
from Server.Indexing.indexing_encryptor import run as encrypt_indexing


def setup_MPC_scripts():
    """

    """

    run([f"cp", f"{compare_and_encrypt_mpc_script_path()}", f"{MP_SDPZ_scripts_directory() / compare_and_encrypt_mpc_script_path().name}"])
    run([f"{MP_SPDZ_compile_path()}", f"{compare_and_encrypt_mpc_script_path().name}", "-F", "128"])
    run([f"cp", f"{compare_and_reencrypt_mpc_script_path()}", f"{MP_SDPZ_scripts_directory() / compare_and_reencrypt_mpc_script_path().name}"])
    run([f"{MP_SPDZ_compile_path()}", f"{compare_and_reencrypt_mpc_script_path().name}", "-F", "128"])



if __name__ == '__main__':
    # Sets the working directory and validates it and MP-SPDZ's path
    working_directory_validation()
    MP_SPDZ_directory_validation()

    # Moves and compiles the MP-SDPZ scripts
    #setup_MPC_scripts()

    # Initializes the database with PNR records
    #create_database(database_size())

    # Creates an inverted index matrix of the database
    create_indexing()

    # Ephemeral encryption of the indexing
    encrypt_indexing()


    server = Server()
    client = Client()
    client.send_init()

    # Creates a new secret database
    #indexing = permute_and_encrypt_database(client)

    # Searching with file retrieval TODO

    server.kill()
    client.kill()
