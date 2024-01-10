from subprocess import run
from json import load
from pathlib import Path
from re import sub
from os import chdir

from Server.Data_Generation.generatePNR_Data import run as generate_data
from Server.Indexing.indexing import run as generate_indexing
from Server.Encoding.index_integer_encoder import run as encode_database_and_indexing
from Server.Indexing.inverted_index_matrix import run as generate_inverse_index_matrix
from Server.Encoding.inverted_index_matrix_integer_encoder import run as encode_database_and_inverse_index_matrix
from Server.Encoding.inverted_index_matrix_integer_encoder import (get_size_of_largest_set_of_pointers)
from Client.Encoding.query_encoder import run as encode_query
from Client.Encoding.file_decoder import run as decode_retrieval

def update_mpc_script():
    """
        Updates the .mpc script with the values required to take the database and indexing as inputs.

        Parameters:
            -

        Returns:
            -
    """

    with open('Server/Indexing/Index_Files/Inverted_Index_Matrix.json', 'r') as f:
        inverted_index_matrix = load(f)
    #number_of_indices = len(inverted_index_matrix.keys())

    with open('Server/Indexing/Index_Files/Indexing.json', 'r') as f:
        indexing = load(f)
    number_of_indices = len(indexing.keys())

    exclude = ['Sample_Record.json']

    with Path('Server/PNR_Records/', mode='r') as f:
        contents = [path for path in f.rglob('*') if path.name not in exclude]
    number_of_files = len(contents)

    with open('MP_SPDZ_Scripts/MP_SPDZ_Only_Scheme.mpc', 'r') as f:
        script = f.read()

    pointer_set_size = get_size_of_largest_set_of_pointers(inverted_index_matrix)
    attribute_set_size = get_size_of_largest_set_of_pointers(indexing)

    script = sub(r'number_of_indices = [\d]*', f'number_of_indices = {number_of_indices}', script)
    script = sub(r'number_of_files = [\d]*', f'number_of_files = {number_of_files}', script)
    script = sub(r'size_of_set_of_pointers = [\d]*', f'size_of_set_of_pointers = {pointer_set_size}', script)
    script = sub(r'size_of_set_of_attributes = [\d]*', f'size_of_set_of_attributes = {attribute_set_size}', script)

    with open('MP_SPDZ_Scripts/MP_SPDZ_Only_Scheme.mpc', 'w') as f:
        f.write(script)

if __name__ == "__main__":
    chdir(Path.cwd().parent)

    generate_data(1)
    generate_indexing()
    generate_inverse_index_matrix()
    encode_database_and_indexing()
    #encode_database_and_inverse_index_matrix()
    encode_query()
    update_mpc_script()
    run(['./Proof_of_Concept_Scheme/compile_and_run.sh'])
    #run(['./Proof_of_Concept_Scheme/run.sh'])
    decode_retrieval()
