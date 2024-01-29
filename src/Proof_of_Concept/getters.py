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


def get_mp_spdz_compile_path() -> Path:
    """ Getter for the mp_spdz_compile_path variable. """
    mp_spdz_compile_path = Path('compile.py')
    return mp_spdz_compile_path


def get_mp_spdz_scripts_path() -> Path:
    """ Getter for the mp_spdz_scripts_path variable. """
    mp_spdz_scripts_path = mp_spdz_directory / 'Programs' / 'Source'
    return mp_spdz_scripts_path


def get_proof_of_concept_mpc_script_path() -> Path:
    """ Getter for the proof_of_concept_mpc_script_path variable. """
    proof_of_concept_mpc_script_path = working_directory.parent / 'MP_SPDZ_Scripts' / 'proof_of_concept.mpc'
    return proof_of_concept_mpc_script_path


def get_client_mp_spdz_outputs_directory() -> Path:
    """ Getter for the client_mp_spdz_outputs_directory variable. """
    global working_directory
    client_mp_spdz_outputs_directory = working_directory / 'Client' / 'MP_SPDZ_Outputs'
    return client_mp_spdz_outputs_directory


def get_client_mp_spdz_inputs_directory() -> Path:
    """ Getter for the client_mp_spdz_inputs_directory variable. """
    global working_directory
    client_mp_spdz_inputs_directory = working_directory / 'Client' / 'MP_SPDZ_Inputs'
    return client_mp_spdz_inputs_directory


def get_server_mp_spdz_inputs_directory() -> Path:
    """ Getter for the server_mp_spdz_inputs_directory variable. """
    global working_directory
    server_mp_spdz_inputs_directory = working_directory / 'Server' / 'MP_SPDZ_Inputs'
    return server_mp_spdz_inputs_directory


def get_server_indexing_directory() -> Path:
    """ getter for the server_indexing_directory variable. """
    global working_directory
    server_indexing_directory = working_directory / 'Server' / 'Indexing'
    return server_indexing_directory


def get_retrieved_records_directory() -> Path:
    """ Getter for the retrieved_records_directory variable. """
    global working_directory
    retrieved_records_directory = working_directory / 'Client' / 'Retrieved_Records'
    return retrieved_records_directory


def get_client_mp_spdz_input_path() -> Path:
    """ Getter for the client_mp_spdz_input_path variable. """
    global working_directory
    client_mp_spdz_input_path = working_directory / 'Client' / 'MP_SPDZ_Inputs' / 'proof_of_concept_Input'
    return client_mp_spdz_input_path


def get_client_mp_spdz_output_path() -> Path:
    """ Getter for the client_mp_spdz_output_path variable. """
    global working_directory
    client_mp_spdz_output_path = working_directory / 'Client' / 'MP_SPDZ_Outputs' / 'proof_of_concept_Output'
    return client_mp_spdz_output_path


def get_encoding_base() -> int:
    """ Getter for the encoding_base variable. """
    encoding_base = 16
    return encoding_base


def get_records_length_upper_bound() -> int:
    """ Getter for the record_length_upper_bound variable. """
    record_length_upper_bound = 6016
    return record_length_upper_bound


def get_inverted_index_matrix_path() -> Path:
    """ Getter for the inverted_index_matrix_path variable. """
    global working_directory
    inverted_index_matrix_path = working_directory / 'Server' / 'Indexing' / 'Inverted_Index_Matrix.json'
    return inverted_index_matrix_path


def get_excluded_records() -> list[str]:
    """ Getter for the excluded_records variable. """
    excluded_records = ['Sample_Record.json']
    return excluded_records


def get_server_mp_spdz_input_path() -> Path:
    """ Getter for the server_mp_spdz_input_path variable. """
    global working_directory
    server_mp_spdz_input_path = working_directory / 'Server' / 'MP_SPDZ_Inputs' / 'proof_of_concept_Input'
    return server_mp_spdz_input_path


def get_indexing_path() -> Path:
    """ Getter for the indexing_path variable. """
    global working_directory
    indexing_path = working_directory / 'Server' / 'Indexing' / 'Indexing.json'
    return indexing_path


def get_supplementary_data_directory() -> Path:
    """ Getter for the supplementary_data_directory variable. """
    global working_directory
    supplementary_data_directory = working_directory / 'Server' / 'Utilities' / 'Data_Generation' / 'Supplementary_Data'
    return supplementary_data_directory


def get_records_directory() -> Path:
    """ Getter for the records_directory variable. """
    global working_directory
    records_directory = working_directory / 'Server' / 'PNR_Records'
    return records_directory


def get_working_directory() -> Path:
    """ Getter for the working_directory variable. """
    return working_directory


def get_mp_spdz_directory() -> Path:
    """ Getter for the mp_spdz_directory variable. """
    return mp_spdz_directory


def get_database_size() -> int:
    """ Getter for the database_size variable. """
    database_size = 4
    return database_size


def get_mp_spdz_protocol() -> str:
    """ Getter for the mp_spdz_protocol variable. """
    mp_spdz_protocol = 'atlas-party.x'
    return mp_spdz_protocol


working_directory = Path.cwd()
mp_spdz_directory = Path.cwd().parent.parent.parent.parent / 'mp-spdz-0.3.8'
