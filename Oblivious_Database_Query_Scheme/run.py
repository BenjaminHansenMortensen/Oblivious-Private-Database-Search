""" Runs the oblivious data query scheme """

from subprocess import run
from Oblivious_Database_Query_Scheme.getters import working_directory_validation, MP_SPDZ_directory_validation
from Oblivious_Database_Query_Scheme.getters import get_MP_SDPZ_compile_path as MP_SPDZ_compile_path
from Oblivious_Database_Query_Scheme.getters import get_database_size as database_size
from Oblivious_Database_Query_Scheme.getters import get_compare_and_encrypt_mpc_script_path as compare_and_encrypt_mpc_script_path
from Oblivious_Database_Query_Scheme.getters import get_compare_and_reencrypt_mpc_script_path as compare_and_reencrypt_mpc_script_path
from Oblivious_Database_Query_Scheme.getters import get_MP_SPDZ_scripts_directory as MP_SDPZ_scripts_directory
from Server.Data_Generation.generatePNR_Data import run as create_database
from Client.Preprocessing.bitonic_sort import bitonic_sort as permute_and_encrypt_database
from Server.Networking.server import Communicate as Server
from Client.Networking.client import Communicate as Client


def setup_MPC_scripts():
    """ """

    run([f"cp", f"{compare_and_encrypt_mpc_script_path()}", f"{MP_SDPZ_scripts_directory() / compare_and_encrypt_mpc_script_path().name}"])
    run([f"{MP_SPDZ_compile_path()}", f"{compare_and_encrypt_mpc_script_path().name}", "-F", "128"])
    run([f"cp", f"{compare_and_reencrypt_mpc_script_path()}", f"{MP_SDPZ_scripts_directory() / compare_and_reencrypt_mpc_script_path().name}"])
    run([f"{MP_SPDZ_compile_path()}", f"{compare_and_reencrypt_mpc_script_path().name}", "-F", "128"])



if __name__ == '__main__':
    # Sets the working directory and validates it and MP-SPDZ's path
    working_directory_validation()
    MP_SPDZ_directory_validation()

    server = Server()
    client = Client()

    # Moves and Compiles the MP-SDPZ scripts
    #setup_MPC_scripts()

    # Initializes the database
    #create_database(database_size())



    # Preprocesses the indexing


    client.send_init()


    #import time

    #start_time = time.time()
    # Creates a new secret database
    #indexing, encryption_keys = permute_and_encrypt_database()
    #for i in range(len(encryption_keys)):
    #    print(f"{i} : {encryption_keys[i][0]}")
    #print(indexing)
    #print("--- %s seconds ---" % (time.time() - start_time))
    #from subprocess import run
    #run("./Oblivious_Database_Query_Scheme/compile_and_run.sh")

    server.kill()
    client.kill()
