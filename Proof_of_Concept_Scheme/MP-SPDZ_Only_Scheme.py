from subprocess import run
from json import load
from pathlib import Path
from re import sub
from os import chdir

from Proof_of_Concept_Scheme.Server.Utilities.Data_Generation.generatePNR_Data import run as generate_data
from Proof_of_Concept_Scheme.Server.Utilities.indexing import run as generate_indexing
from Proof_of_Concept_Scheme.Server.Utilities.index_integer_encoder import run as encode_database_and_indexing
from Proof_of_Concept_Scheme.Server.Utilities.inverted_index_matrix import run as generate_inverse_index_matrix
from Proof_of_Concept_Scheme.Server.Utilities.inverted_index_matrix_integer_encoder import (get_size_of_largest_set_of_pointers)
from Proof_of_Concept_Scheme.Client.Utilities.query_encoder import run as encode_query
from Proof_of_Concept_Scheme.Client.Utilities.file_decoder import run as decode_retrieval


def setup_directories():
    """

    """

    Path("Server/Indexing").mkdir(exist_ok=True)
    Path("Server/MP_SPDZ_Inputs").mkdir(exist_ok=True)
    Path("Client/Retrieved_Records").mkdir(exist_ok=True)
    Path("Client/MP_SPDZ_Inputs").mkdir(exist_ok=True)
    Path("Client/MP_SPDZ_Outputs").mkdir(exist_ok=True)

def update_mpc_script():
    """
        Updates the .mpc script with the values required to take the database and indexing as inputs.

        Parameters:
            -

        Returns:
            -
    """

    with open('Server/Indexing/Inverted_Index_Matrix.json', 'r') as f:
        inverted_index_matrix = load(f)
    #number_of_indices = len(inverted_index_matrix.keys())

    with open('Server/Indexing/Indexing.json', 'r') as f:
        indexing = load(f)
    number_of_indices = len(indexing.keys())

    exclude = ['Sample_Record.json']

    with Path('Server/PNR_Records/', mode='r') as f:
        contents = [path for path in f.rglob('*') if path.name not in exclude]
    number_of_files = len(contents)

    with open('../MP_SPDZ_Scripts/MP_SPDZ_Only_Scheme.mpc', 'r') as f:
        script = f.read()

    pointer_set_size = get_size_of_largest_set_of_pointers(inverted_index_matrix)
    attribute_set_size = get_size_of_largest_set_of_pointers(indexing)

    script = sub(r'number_of_indices = [\d]*', f'number_of_indices = {number_of_indices}', script)
    script = sub(r'number_of_files = [\d]*', f'number_of_files = {number_of_files}', script)
    script = sub(r'size_of_set_of_pointers = [\d]*', f'size_of_set_of_pointers = {pointer_set_size}', script)
    script = sub(r'size_of_set_of_attributes = [\d]*', f'size_of_set_of_attributes = {attribute_set_size}', script)

    with open('../MP_SPDZ_Scripts/MP_SPDZ_Only_Scheme.mpc', 'w') as f:
        f.write(script)

if __name__ == "__main__":
    chdir(Path.cwd())

    setup_directories()

    generate_data(1)
    generate_indexing()
    generate_inverse_index_matrix()
    encode_database_and_indexing()
    #encode_database_and_inverse_index_matrix()
    encode_query()
    update_mpc_script()
    run(['./compile_and_run.sh'])
    decode_retrieval()
