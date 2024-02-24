""" The getters for the different variables used by the application. """

# Imports.
from pathlib import Path
from os import chdir


def working_directory_validation() -> None:
    """
        Validates the path to the Oblivious Database Query directory.

        Parameters:
            -

        Returns:
            :raises Exception
            -
    """

    global working_directory

    try:
        chdir(working_directory)
    except Exception as e:
        print(f'Error occurred in validating the working directory. {e}')


def mp_spdz_directory_validation() -> None:
    """
        Validates the path to the MP-SPDZ directory.

        Parameters:
            -

        Returns:
            :raises NotADirectoryError
            -
    """

    global mp_spdz_directory

    if not mp_spdz_directory.is_dir() or not mp_spdz_directory.exists():
        raise NotADirectoryError('The MP-SPDZ path is not valid.')


def get_server_ip() -> str:
    """ Getter for the server_ip variable. """
    global server_ip
    return server_ip


def get_server_port() -> int:
    """ Getter for the server_port variable. """
    global server_port
    return server_port


def get_client_ip() -> str:
    """ Getter for the client_ip variable. """
    global client_ip
    return client_ip


def get_client_port() -> int:
    """ Getter for the client_ip variable. """
    global client_port
    return client_port


def get_encoding_base() -> int:
    """ Getter for the encoding_base variable. """
    encoding_base = 16
    return encoding_base


def get_number_of_bytes() -> int:
    """ Getter for the number_of_bytes variable. """
    block_size = get_block_size()
    number_of_bytes = block_size // 8
    return number_of_bytes


def get_max_file_length() -> int:
    """ Getter for the max_file_length variable. """
    max_file_length = 6016
    return max_file_length


def get_max_amount_of_attributes_per_record() -> int:
    """ Getter for the max_amount_of_attributes_per_record variable. """
    max_amount_of_attributes_per_record = 368
    return max_amount_of_attributes_per_record


def get_embedding_dimension() -> int:
    """ Getter for the embedding_dimension variable. """
    embedding_dimension = 768
    return embedding_dimension


def get_embedding_model() -> str:
    """ Getter for the embedding_model variable. """
    embedding_model = 'all-mpnet-base-v2'
    return embedding_model


def get_float_to_integer_scalar() -> int:
    """ Getter for the float_to_integer_scalar variable."""
    float_to_integer_scalar = 10**9
    return float_to_integer_scalar


def get_semantic_search_request_threshold() -> int:
    """ Getter for the semantic_search_request_threshold variable. """
    semantic_search_request_threshold = 1
    return semantic_search_request_threshold


def get_semantic_search_mpc_script_path() -> Path:
    """ Getter for the semantic_search_mpc_script_path variable. """
    semantic_search_mpc_script_path = get_application_mp_spdz_scripts_directory() / 'semantic_search.mpc'
    return semantic_search_mpc_script_path


def get_number_of_blocks() -> int:
    """ Getter for the number_of_blocks variable. """
    number_of_blocks = get_max_file_length() // get_encoding_base()
    return number_of_blocks


def get_working_directory() -> Path:
    """ Getter for the working_directory variable. """
    global working_directory
    return working_directory


def get_mp_spdz_directory() -> Path:
    """ Getter for the MP_SPDZ_directory variable. """
    global mp_spdz_directory
    return mp_spdz_directory


def get_server_utilities_directory() -> Path:
    """ Getter for the server_utilities_directory variable. """
    server_utilities_directory = get_server_directory() / 'Utilities'
    return server_utilities_directory


def get_server_data_generation_directory() -> Path:
    """ Getter for the server_data_generation_directory variable. """
    server_data_generation_directory = get_server_utilities_directory() / 'Data_Generation'
    return server_data_generation_directory


def get_supplementary_data_directory() -> Path:
    """ Getter for the supplementary_data_directory variable. """
    supplementary_data_directory = get_server_data_generation_directory() / 'Supplementary_Data'
    return supplementary_data_directory


def get_block_size() -> int:
    """ Getter for the block_size variable. """
    block_size = 128
    return block_size


def get_hex_block_size() -> int:
    """ Getter for the hex_block_size variable. """
    hex_block_size = 32
    return hex_block_size


def get_records_directory() -> Path:
    """ Getter for the records_directory variable. """
    records_directory = get_server_directory() / 'Records'
    return records_directory


def get_excluded_records() -> list:
    """ Getter for the excluded_records variable. """
    excluded_records = ['Sample_Record.json']
    return excluded_records


def get_encrypted_records_directory() -> Path:
    """ Getter for the encrypted_records_directory variable. """
    encrypted_records_directory = get_server_directory() / 'Encrypted_Records'
    return encrypted_records_directory


def get_client_mp_spdz_input_directory() -> Path:
    """ Getter for the client_mp_spdz_input_directory variable. """
    client_mp_spdz_input_directory = get_client_directory() / 'MP_SPDZ_Inputs'
    return client_mp_spdz_input_directory


def get_client_mp_spdz_input_path() -> Path:
    """ Getter for the client_mp_spdz_input_file variable. """
    client_mp_spdz_input_path = get_client_mp_spdz_input_directory() / 'Client_Input'
    return client_mp_spdz_input_path


def get_client_mp_spdz_output_directory() -> Path:
    """ Getter for the client_mp_spdz_output_directory variable. """
    client_mp_spdz_output_directory = get_client_directory() / 'MP_SPDZ_Outputs'
    return client_mp_spdz_output_directory


def get_client_mp_spdz_output_path() -> Path:
    """ Getter for the client_mp_spdz_output_path variable. """
    client_mp_spdz_output_path = get_client_mp_spdz_output_directory() / 'Client_Output'
    return client_mp_spdz_output_path


def get_server_mp_spdz_input_directory() -> Path:
    """ Getter for the server_mp_spdz_input_directory variable. """
    server_mp_spdz_input_directory = get_server_directory() / 'MP_SPDZ_Inputs'
    return server_mp_spdz_input_directory


def get_server_mp_spdz_input_path() -> Path:
    """ Getter for the server_mp_spdz_input_path variable. """
    server_mp_spdz_input_path = get_server_mp_spdz_input_directory() / 'Server_Input'
    return server_mp_spdz_input_path


def get_server_mp_spdz_output_directory() -> Path:
    """ Getter for the server_mp_spdz_output_directory variable. """
    server_mp_spdz_output_directory = get_server_directory() / 'MP_SPDZ_Outputs'
    return server_mp_spdz_output_directory


def get_server_mp_spdz_output_path() -> Path:
    """ Getter for the server_mp_spdz_output_path variable. """
    server_mp_spdz_output_path = get_server_mp_spdz_output_directory() / 'Server_Output'
    return server_mp_spdz_output_path


def get_application_mp_spdz_scripts_directory() -> Path:
    """ Getter for the application_mp_spdz_scripts_directory variable. """
    global working_directory
    application_mp_spdz_scripts_directory = working_directory.parent / 'MP_SPDZ_Scripts'
    return application_mp_spdz_scripts_directory


def get_sort_and_encrypt_with_circuit_mpc_script_path() -> Path:
    """ Getter for the sort_and_encrypt_with_circuit variable. """
    sort_and_encrypt_with_circuit_path = (get_application_mp_spdz_scripts_directory() /
                                          f'sort_and_encrypt_with_circuit.mpc')
    return sort_and_encrypt_with_circuit_path


def get_sort_and_reencrypt_with_circuit_mpc_script_path() -> Path:
    """ Getter for the sort_and_reencrypt_with_circuit_mpc_script_path variable. """
    sort_and_reencrypt_with_circuit_mpc_script_path = (get_application_mp_spdz_scripts_directory() /
                                                       f'sort_and_reencrypt_with_circuit.mpc')
    return sort_and_reencrypt_with_circuit_mpc_script_path


def get_aes_128_ecb_with_circuit_mpc_script_path() -> Path:
    """ Getter for the aes_128_ecb_with_circuit_mpc_script_path variable. """
    aes_128_ecb_with_circuit_mpc_script_path = (get_application_mp_spdz_scripts_directory() /
                                                'aes_128_ecb_with_circuit.mpc')
    return aes_128_ecb_with_circuit_mpc_script_path


def get_application_mp_spdz_circuits_directory() -> Path:
    """ Getter for the application_mp_spdz_circuits_directory variable. """
    global working_directory
    application_mp_spdz_circuits_directory = working_directory.parent / 'MP_SPDZ_Circuits'
    return application_mp_spdz_circuits_directory


def get_if_else_circuit_path() -> Path:
    """ Getter for the if_else_circuit_path variable. """
    if_else_circuit_path = get_application_mp_spdz_circuits_directory() / f'if_else{get_block_size()}.txt'
    return if_else_circuit_path


def get_sort_and_encrypt_circuit_path() -> Path:
    """ Getter for the sort_and_encrypt_circuit variable. """
    sort_and_encrypt_circuit = get_application_mp_spdz_circuits_directory() / f'sort_and_encrypt{get_block_size()}.txt'
    return sort_and_encrypt_circuit


def get_sort_and_reencrypt_circuit_path() -> Path:
    """ Getter for the sort_and_reencrypt_circuit variable. """
    sort_and_reencrypt_circuit = (get_application_mp_spdz_circuits_directory() /
                                  f'sort_and_reencrypt{get_block_size()}.txt')
    return sort_and_reencrypt_circuit


def get_mp_spdz_programs_directory() -> Path:
    """ Getter for the mp_spdz_programs_directory variable. """
    global  mp_spdz_directory
    mp_spdz_programs_directory = mp_spdz_directory / 'Programs'
    return mp_spdz_programs_directory


def get_mp_spdz_scripts_directory() -> Path:
    """ Getter for the mp_spdz_scripts_directory variable. """
    mp_spdz_scripts_path = get_mp_spdz_programs_directory() / 'Source'
    return mp_spdz_scripts_path


def get_mp_spdz_circuits_directory() -> Path:
    """ Getter for the MP_SPDZ_circuits_directory variable. """
    mp_spdz_circuits_path = get_mp_spdz_programs_directory() / 'Circuits'
    return mp_spdz_circuits_path


def get_mp_spdz_compile_path() -> Path:
    """ Getter for the MP_SPDZ_compile_path variable. """
    global mp_spdz_directory
    mp_spdz_compile_path = mp_spdz_directory / 'compile.py'
    return mp_spdz_compile_path


def get_inverted_index_matrix_path() -> Path:
    """ Getter for the inverted_index_matrix_path variable. """
    inverted_index_matrix_path = get_server_indexing_directory() / 'Inverted_Index_Matrix.json'
    return inverted_index_matrix_path


def get_server_encrypted_inverted_index_matrix_directory() -> Path:
    """ Getter for the server_encrypted_inverted_index_matrix_directory variable. """
    server_encrypted_inverted_index_matrix_directory = (get_server_indexing_directory() /
                                                        'Encrypted_Inverted_Index_Matrix')
    return server_encrypted_inverted_index_matrix_directory


def get_client_indexing_directory() -> Path:
    """ Getter for the client_indexing_directory variable. """
    client_indexing_directory = get_client_directory() / 'Indexing'
    return client_indexing_directory


def get_client_encrypted_inverted_index_matrix_directory() -> Path:
    """ Getter for the client_encrypted_inverted_index_matrix_directory variable. """
    client_encrypted_inverted_index_matrix_directory = (get_client_indexing_directory() /
                                                        'Encrypted_Inverted_Index_Matrix')
    return client_encrypted_inverted_index_matrix_directory


def get_encrypted_inverted_index_matrix_attribute_limit() -> int:
    """ Getter for the encrypted_inverted_index_matrix_attribute_limit variable. """
    encrypted_inverted_index_matrix_attribute_limit = 10**5
    return encrypted_inverted_index_matrix_attribute_limit


def get_permutation_indexing_path() -> Path:
    """ Getter for the permutation_indexing_path variable. """
    permutation_indexing_path = get_client_indexing_directory() / 'Permutation_Indexing.json'
    return permutation_indexing_path


def get_retrieved_records_directory() -> Path:
    """ Getter for the retrieved_records_directory variable. """
    retrieved_records_directory = get_client_directory() / 'Retrieved_Records'
    return retrieved_records_directory


def get_client_directory() -> Path:
    """ Getter for the client_directory variable. """
    global working_directory
    client_directory = working_directory / 'Client'
    return client_directory


def get_records_encryption_key_streams_directory() -> Path:
    """ Getter for the records_encryption_keys_directory variable. """
    records_encryption_keys_directory = get_client_directory() / 'Records_Encryption_Key_Streams'
    return records_encryption_keys_directory


def get_mp_spdz_player_data_directory():
    """ Getter for the mp_spdz_player_data_directory variable. """
    global mp_spdz_directory
    mp_spdz_player_data_directory = mp_spdz_directory / 'Player-Data'
    return mp_spdz_player_data_directory


def get_client_networking_key_path() -> Path:
    """ Getter for the client_networking_key_path variable. """
    client_networking_key_path = get_mp_spdz_player_data_directory() / 'P0.key'
    return client_networking_key_path


def get_client_networking_certificate_path() -> Path:
    """ Getter for the client_networking_key_path variable. """
    client_networking_certificate_path = get_mp_spdz_player_data_directory() / 'P0.pem'
    return client_networking_certificate_path


def get_server_networking_key_path() -> Path:
    """ Getter for the server_networking_key_path variable. """
    server_networking_key_path = get_mp_spdz_player_data_directory() / 'P1.key'
    return server_networking_key_path


def get_server_networking_certificate_path() -> Path:
    """ Getter for the client_networking_key_path variable. """
    server_networking_certificate_path = get_mp_spdz_player_data_directory() / 'P1.pem'
    return server_networking_certificate_path


def get_server_encryption_keys_directory() -> Path:
    """ Getter for the server_encryption_keys_directory variable. """
    server_encryption_keys_directory = get_server_directory() / 'Encryption_Keys'
    return server_encryption_keys_directory


def get_inverted_index_matrix_encryption_key_path() -> Path:
    """ Getter for the inverted_index_matrix_encryption_key_path variable. """
    inverted_index_matrix_encryption_key_path = get_server_encryption_keys_directory() / 'Encryption_Key.txt'
    return inverted_index_matrix_encryption_key_path


def get_requested_indices_path() -> Path:
    """ Getter for the requested_indices_path variable. """
    requested_indices_path = get_client_indexing_directory() / 'Requested_Indices.txt'
    return requested_indices_path


def get_server_directory() -> Path:
    """ Getter for the server_directory variable. """
    global working_directory
    server_directory = working_directory / 'Server'
    return server_directory


def get_server_indexing_directory() -> Path:
    """ Getter for the server_indexing_directory variable. """
    server_indexing_directory = get_server_directory() / 'Indexing'
    return server_indexing_directory


def get_server_semantic_indexing_path() -> Path:
    """ Getter for the server_semantic_indexing_path variable. """
    server_semantic_indexing_path = get_server_indexing_directory() / 'Semantic_Indexing.json'
    return server_semantic_indexing_path


def get_client_number_of_dummy_items_path() -> Path:
    """ Getter for the client_number_of_dummy_items_path variable. """
    client_number_of_dummy_items_path = get_client_indexing_directory() / 'number_of_dummy_items.txt'
    return client_number_of_dummy_items_path


def get_server_record_pointers_path() -> Path:
    """ Getter for the server_record_pointers_path variable. """
    server_record_pointers_path = get_server_indexing_directory() / 'Record_Pointers.json'
    return server_record_pointers_path


def get_number_of_dummy_items() -> int:
    """ Getter for the number_of_dummy_items variable. """
    number_of_dummy_items = get_database_size() - get_number_of_records()
    return number_of_dummy_items


def get_database_size() -> int:
    """ Getter for the database_size variable. """
    database_size = 2**4
    return database_size


def get_number_of_records() -> int:
    """ Getter for the number_of_records variable. """
    number_of_records = 10
    return number_of_records


def get_mp_spdz_protocol() -> str:
    """ Getter for the mp_spdz_protocol variable. """
    mp_spdz_protocol = 'semi-party.x'
    return mp_spdz_protocol


working_directory = Path(__file__).parent
mp_spdz_directory = Path('/home/mpc2/mp-spdz-0.3.8')
server_ip = 'localhost'
server_port = 5500
client_ip = 'localhost'
client_port = 5005
