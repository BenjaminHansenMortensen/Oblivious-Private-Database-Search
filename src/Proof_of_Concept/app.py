""" Runs the applicaiton. """


# Imports.
from subprocess import run, Popen, PIPE
from json import load
from pathlib import Path
from re import sub
from os import chdir

# Local getter imports.
from Proof_of_Concept.getters import get_working_directory as working_directory
from Proof_of_Concept.getters import get_mp_spdz_directory as mp_spdz_directory
from Proof_of_Concept.getters import (get_database_size as
                                      database_size)
from Proof_of_Concept.getters import (get_server_indexing_directory as
                                      server_indexing_directory)
from Proof_of_Concept.getters import (get_server_mp_spdz_inputs_directory as
                                      server_mp_spdz_inputs_directory)
from Proof_of_Concept.getters import (get_retrieved_records_directory as
                                      retrieved_records_directory)
from Proof_of_Concept.getters import (get_client_mp_spdz_inputs_directory as
                                      client_mp_spdz_inputs_directory)
from Proof_of_Concept.getters import (get_client_mp_spdz_outputs_directory as
                                      client_mp_spdz_outputs_directory)
from Proof_of_Concept.getters import (get_inverted_index_matrix_path as
                                      inverted_index_matrix_path)
from Proof_of_Concept.getters import (get_indexing_path as
                                      indexing_path)
from Proof_of_Concept.getters import (get_records_directory as
                                      records_directory)
from Proof_of_Concept.getters import (get_proof_of_concept_mpc_script_path as
                                      proof_of_concept_mpc_script_path)
from Proof_of_Concept.getters import (get_mp_spdz_scripts_path as
                                      mp_spdz_scripts_path)
from Proof_of_Concept.getters import (get_mp_spdz_compile_path as
                                      mp_spdz_compile_path)
from Proof_of_Concept.getters import (get_client_mp_spdz_input_path as
                                      client_mp_spdz_input_path)
from Proof_of_Concept.getters import (get_client_mp_spdz_output_path as
                                      client_mp_spdz_output_path)
from Proof_of_Concept.getters import (get_server_mp_spdz_input_path as
                                      server_mp_spdz_input_path)
from Proof_of_Concept.getters import (get_records_length_upper_bound as
                                      records_length_upper_bound)
from Proof_of_Concept.getters import (get_mp_spdz_protocol as
                                      mp_spdz_protocol)
from Proof_of_Concept.getters import (get_excluded_records as
                                      excluded_records)


# Client and Server imports.
from Proof_of_Concept.Server.Utilities.Data_Generation.generate_passenger_number_records import run as generate_data
from Proof_of_Concept.Server.Utilities.indexing import run as generate_indexing
from Proof_of_Concept.Server.Utilities.index_integer_encoder import run as encode_database_and_indexing
from Proof_of_Concept.Server.Utilities.inverted_index_matrix import run as generate_inverse_index_matrix
from Proof_of_Concept.Server.Utilities.inverted_index_matrix_integer_encoder import get_size_of_largest_set_of_pointers
from Proof_of_Concept.Server.Utilities.inverted_index_matrix_integer_encoder import run as encode_database_and_inverse_index_matrix
from Proof_of_Concept.Client.Utilities.query_encoder import run as encode_query
from Proof_of_Concept.Client.Utilities.file_decoder import run as decode_retrieval


def clean_up_files() -> None:
    """
        Removes records created from previous execution.

        Parameters:
            -

        Returns:
            :raises
            -
    """

    # Removes the stored PNR records.
    file_paths = [path for path in records_directory().glob('*') if (path.name not in excluded_records())]
    for file_path in file_paths:
        file_path.unlink()

    # Removes the stored indexing records.
    file_paths = [path for path in server_indexing_directory().rglob('*') if path.is_file()]
    for file_path in file_paths:
        file_path.unlink()

    # Removes the stored retrieved indices.
    file_paths = [path for path in retrieved_records_directory().glob('*')]
    for file_path in file_paths:
        file_path.unlink()

    return


def setup_directories() -> None:
    """
        Creates the necessary directories.

        Parameters:
            -

        Returns:
            :raises
            -
    """

    server_indexing_directory().mkdir(exist_ok=True)
    server_mp_spdz_inputs_directory().mkdir(exist_ok=True)
    retrieved_records_directory().mkdir(exist_ok=True)
    client_mp_spdz_inputs_directory().mkdir(exist_ok=True)
    client_mp_spdz_outputs_directory().mkdir(exist_ok=True)
    records_directory().mkdir(exist_ok=True)

    return


def update_mpc_script(use_inverted_index_matrix: bool) -> None:
    """
        Updates the .mpc script with the values required to take the database and indexing as inputs.

        Parameters:
            - use_inverted_index_matrix (bool) : User's response to whether to use an inverted index matrix or not.

        Returns:
            :raises
            -
    """

    with inverted_index_matrix_path().open('r') as f:
        inverted_index_matrix = load(f)
        f.close()

    with indexing_path().open('r') as f:
        indexing = load(f)
        f.close()

    if not use_inverted_index_matrix:
        number_of_indices = len(indexing.keys())
    else:
        number_of_indices = len(inverted_index_matrix.keys())

    number_of_files = database_size()

    with proof_of_concept_mpc_script_path().open('r') as f:
        script = f.read()
        f.close()

    pointer_set_size = get_size_of_largest_set_of_pointers(inverted_index_matrix)
    attribute_set_size = get_size_of_largest_set_of_pointers(indexing)

    script = sub(r'number_of_indices = \d*', f'number_of_indices = {number_of_indices}', script)
    script = sub(r'number_of_files = \d*', f'number_of_files = {number_of_files}', script)
    script = sub(r'file_size_length_upper_bound = \d*', f'file_size_length_upper_bound = {records_length_upper_bound()}', script)
    script = sub(r'size_of_set_of_pointers = \d*', f'size_of_set_of_pointers = {pointer_set_size}', script)
    script = sub(r'size_of_set_of_attributes = \d*', f'size_of_set_of_attributes = {attribute_set_size}', script)

    if not use_inverted_index_matrix:
        script = sub(r'#test_searching_retrieval\(\)[^:]', f'test_searching_retrieval()\n', script)
        script = sub(r'[^#]test_inverse_searching_retrieval\(\)[^:]', f'\n#test_inverse_searching_retrieval()\n', script)
        script = sub(r'[^#]test_inverse_searching_oram_retrival\(\)[^:]', f'\n#test_inverse_searching_oram_retrival()\n', script)
        script = sub(r'[^#]test_inverse_searching_oram_retrival_oram\(\)[^:]', f'\n#test_inverse_searching_oram_retrival_oram()\n', script)
    else:
        script = sub(r'[^#]test_searching_retrieval\(\)[^:]', f'\n#test_searching_retrieval()\n', script)
        script = sub(r'#test_inverse_searching_retrieval\(\)[^:]', f'test_inverse_searching_retrieval()\n', script)
        script = sub(r'[^#]test_inverse_searching_oram_retrival\(\)[^:]', f'\n#test_inverse_searching_oram_retrival()\n', script)
        script = sub(r'[^#]test_inverse_searching_oram_retrival_oram\(\)[^:]', f'\n#test_inverse_searching_oram_retrival_oram()\n', script)

    with open('../MP_SPDZ_Scripts/proof_of_concept.mpc', 'w') as f:
        f.write(script)
        f.close()

    return


def compile_and_run_mp_spdz():
    """

    """

    run(['cp', proof_of_concept_mpc_script_path(), f'{mp_spdz_scripts_path()}/{proof_of_concept_mpc_script_path().name}'])
    chdir(mp_spdz_directory())
    run([f'{mp_spdz_directory() / mp_spdz_compile_path().name}', proof_of_concept_mpc_script_path().stem])
    client = Popen([f'{mp_spdz_directory() / mp_spdz_protocol()}', f'{proof_of_concept_mpc_script_path().stem}',
                    '-p', '0',
                    '-IF', f'{client_mp_spdz_input_path()}',
                    '-OF', f'{client_mp_spdz_output_path()}'
                    ], stdout=PIPE, stderr=PIPE)
    server = Popen([f'{mp_spdz_directory() / mp_spdz_protocol()}', f'{proof_of_concept_mpc_script_path().stem}',
                    '-p', '1',
                    '-IF',
                    f'{server_mp_spdz_input_path()}'
                    ], stdout=PIPE, stderr=PIPE)
    empty = Popen([f'{mp_spdz_directory() / mp_spdz_protocol()}', f'{proof_of_concept_mpc_script_path().stem}',
                   '-p', '2',
                   ], stdout=PIPE, stderr=PIPE)

    client_output, client_error = client.communicate()
    server_output, server_error = server.communicate()
    empty_output, empty_error = empty.communicate()

    client.kill()
    server.kill()
    empty.kill()

    chdir(working_directory())


def main() -> None:
    """
        Runs the application.

        Parameters:
            -

        Returns:
            :raises
            -
    """

    clean_up_files()

    use_inverted_index_matrix = input("Use an inverted index matrix for record indexing?: (y/n) ")

    if use_inverted_index_matrix == 'y':
        use_inverted_index_matrix = True
    else:
        use_inverted_index_matrix = False

    chdir(Path.cwd())

    setup_directories()

    generate_data(database_size())
    generate_indexing()
    generate_inverse_index_matrix()
    if not use_inverted_index_matrix:
        encode_database_and_indexing()
    else:
        encode_database_and_inverse_index_matrix()

    search_query = input("Search Query: ")
    encode_query(search_query)
    update_mpc_script(use_inverted_index_matrix)
    compile_and_run_mp_spdz()
    decode_retrieval()

    return


main()
