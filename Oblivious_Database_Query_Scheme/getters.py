""" The getters for the different variables used by the Oblivious Database Query Scheme """

from pathlib import Path
from os import chdir


def working_directory_validation():
    """
        Validates the path to the Oblivious Database Query directory.

        Parameters:
            -

        Returns:
            :raises Exception, NotADirectoryError
            - working_directory (Path) : The path to where the application will work from.
    """

    working_dir = get_working_directory()

    try:
        chdir(working_dir)
    except Exception:
        print("Could not set a new working directory.")


def MP_SPDZ_directory_validation() -> Path:
    """
        Validates the path to the MP-SPDZ directory.

        Parameters:
            -

        Returns:
            :raises Exception, NotADirectoryError
            - MP_SPDZ_directory (Path) : The path to the MP-SPDZ directory.
    """

    MP_SPDZ_directory = get_MP_SPDZ_directory()

    if not MP_SPDZ_directory.is_dir() or not MP_SPDZ_directory.exists():
        raise NotADirectoryError("The MP-SPDZ path is not valid.")

    return MP_SPDZ_directory


def get_encoding_base() -> int:
    """ Getter for the encoding_base variable """
    encoding_base = 16
    return encoding_base

def get_number_of_bytes() -> int:
    """ Getter for the number_of_bytes variable"""
    block_size = get_block_size()
    number_of_bytes = block_size // 8
    return number_of_bytes

def get_max_file_length() -> int:
    """ Getter for the max_file_length variable """
    max_file_length = 6016
    return max_file_length


def get_number_of_blocks() -> int:
    """ Getter for the number_of_blocks variable """
    number_of_blocks = get_max_file_length() // get_encoding_base()
    return number_of_blocks


def get_database_size() -> int:
    """ Getter for the database_size variable """
    database_size = 2**3
    return database_size


def get_MP_SPDZ_directory() -> Path:
    """ Getter for the MP_SPDZ_directory variable """
    MP_SPDZ_directory = MP_SPDZ_directory_validation()
    return MP_SPDZ_directory


def get_working_directory() -> Path:
    """ Getter for the working_directory variable """
    global working_directory
    return working_directory


def get_MP_SPDZ_directory() -> Path:
    """ Getter for the MP_SPDZ_directory variable """
    global MP_SPDZ_directory
    return MP_SPDZ_directory

def get_block_size() -> int:
    """ Getter for the block_size variable """
    block_size = 128
    return block_size


def get_PNR_records_directory() -> Path:
    """ Getter for the PNR records path """
    directory = get_working_directory() / "Server" / "PNR_Records"
    return directory


def get_excluded_PNR_records() -> list:
    """ Getter for the excluded_PNR_records list """
    excluded_PNR_records = ['Sample_Record.json']
    return excluded_PNR_records

def get_encrypted_PNR_records_directory() -> Path:
    """ Getter for the encrypted_PNR_records_directory variable """
    global working_directory
    encrypted_PNR_records_directory = working_directory / "Server" / "Encrypted_PNR_Records"
    return encrypted_PNR_records_directory


def get_client_MP_SPDZ_input_path() -> Path:
    """ Getter for the client_MP_SPDZ_input_file path """
    global working_directory
    client_MP_SPDZ_input_path = working_directory / "Client" / "MP_SPDZ_Inputs" / "Client_Input"
    return client_MP_SPDZ_input_path

def get_client_MP_SPDZ_output_path() -> Path:
    """ Getter for the client_MP_SPDZ_output_file path """
    global working_directory
    client_MP_SPDZ_output_path = working_directory / "Client" / "MP_SPDZ_Outputs" / "Client_Output"
    return client_MP_SPDZ_output_path


def get_server_MP_SPDZ_input_path() -> Path:
    """ Getter for the server_MP_SPDZ_input_file path """
    global working_directory
    server_MP_SPDZ_input_path = working_directory / "Server" / "MP_SPDZ_Inputs" / "Server_Input"
    return server_MP_SPDZ_input_path


def get_server_MP_SPDZ_output_path() -> Path:
    """ Getter for the server_MP_SPDZ_output_file path variable """
    global working_directory
    server_MP_SPDZ_output_path = working_directory / "Server" / "MP_SPDZ_Outputs" / "Server_Output"
    return server_MP_SPDZ_output_path


def get_compare_and_encrypt_mpc_script_path():
    """ Getter for the compare_and_encrypt_script_path variable """
    global working_directory
    compare_and_encrypt_script_path = working_directory / "MP_SPDZ_Scripts" / "compare_and_encrypt.mpc"
    return compare_and_encrypt_script_path


def get_compare_and_reencrypt_mpc_script_path():
    """ Getter for the compare_and_encrypt_script_path variable """
    global working_directory
    compare_and_encrypt_script_path = working_directory / "MP_SPDZ_Scripts" / "compare_and_reencrypt.mpc"
    return compare_and_encrypt_script_path


def get_aes_128_mpc_script_path():
    """ Getter for the aes_128_mpc_script_path variable """
    global working_directory
    aes_128_mpc_script_path = working_directory / "MP_SPDZ_Scripts" / "aes_128.mpc"
    return aes_128_mpc_script_path


def get_MP_SPDZ_scripts_directory():
    """ Getter for the MP_SPDZ_scripts_directory in the MP_SPDZ directory """
    global MP_SPDZ_directory
    MP_SPDZ_scripts_path = MP_SPDZ_directory / "Programs" / "Source"
    return MP_SPDZ_scripts_path


def get_MP_SDPZ_compile_path():
    """ Getter for the MP_SPDZ_compile_path variable """
    global MP_SPDZ_directory
    MP_SPDZ_compile_path = MP_SPDZ_directory / "compile.py"
    return MP_SPDZ_compile_path

def get_inverted_index_matrix_path():
    """ Getter for the inverted_index_matrix_path variable """
    global working_directory
    inverted_index_matrix_path = working_directory / "Server" / "Indexing" / "Index_Files" / "Inverted_Index_Matrix.json"
    return inverted_index_matrix_path

def get_encrypted_inverted_index_matrix_path():
    """ Getter for the encrypted_inverted_index_matrix_path variable """
    global working_directory
    encrypted_inverted_index_matrix_path = working_directory / "Server" / "Indexing" / "Index_Files" / "Encrypted_Inverted_Index_Matrix.json"
    return encrypted_inverted_index_matrix_path

def get_permutation_indexing_path():
    """ Getter for the permutation_indexing_path variable """
    global working_directory
    permutation_indexing_path = working_directory / "Client" / "Indexing" / "Permutation_Indexing.json"
    return permutation_indexing_path

def get_retrieved_records_directory():
    """ Getter for the retrieved_records_directory variable"""
    global working_directory

    retrieved_records_directory = working_directory / "Client" / "Retrieved_Records"
    return retrieved_records_directory

def get_records_encryption_key_streams_directory():
    """ Getter for the records_encryption_keys_directory """
    global working_directory
    records_encryption_keys_directory = working_directory / "Client" / "Records_Encryption_Key_Streams"
    return records_encryption_keys_directory


working_directory = Path.cwd().parent
MP_SPDZ_directory = Path.cwd().parent.parent.parent / "mp-spdz-0.3.8"
