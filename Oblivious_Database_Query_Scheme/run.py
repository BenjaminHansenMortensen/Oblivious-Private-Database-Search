""" Runs the oblivious data query scheme """

from subprocess import run
from Oblivious_Database_Query_Scheme.getters import working_directory_validation, MP_SPDZ_directory_validation
from Oblivious_Database_Query_Scheme.getters import get_MP_SDPZ_compile_path as MP_SPDZ_compile_path
from Oblivious_Database_Query_Scheme.getters import get_database_size as database_size
from Oblivious_Database_Query_Scheme.getters import get_xor_mpc_script_path as xor_mpc_script_path
from Oblivious_Database_Query_Scheme.getters import get_MP_SPDZ_scripts_directory as MP_SDPZ_scripts_directory
from Server.Data_Generation.generatePNR_Data import run as create_database
from Client.Preprocessing.bitonic_sort import bitonic_sort as permute_and_encrypt_database


def setup_MPC_scripts():
    """ """

    move_xor_script = run([f"cp", f"{xor_mpc_script_path()}", f"{MP_SDPZ_scripts_directory() / xor_mpc_script_path().name}"])
    compile_xor_script = run([f"{MP_SPDZ_compile_path()}", f"{xor_mpc_script_path().name}", "-F", "128"])


if __name__ == '__main__':
    # Sets the working directory and validates it and MP-SPDZ's path
    working_directory_validation()
    MP_SPDZ_directory_validation()

    # Moves and Compiles the MP-SDPZ scripts
    setup_MPC_scripts()

    # Initializes the database
    #create_database(database_size())

    # Preprocesses the indexing and AES key_streams

    # Creates a new secret database
    indexing = permute_and_encrypt_database()

    #from subprocess import run
    #run("./Oblivious_Database_Query_Scheme/compile_and_run.sh")
