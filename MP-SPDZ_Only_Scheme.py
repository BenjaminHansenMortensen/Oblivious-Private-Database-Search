from subprocess import run
from json import load
from pathlib import Path
from re import sub

from Server.MockData.generatePNR_Data import run as generate_data
from Server.DatabaseIndex.invertedIndexMatrix import run as generate_inverse_index_matrix
from Server.DatabaseIndex.fileIndexing import run as generate_indexing
from Server.DatabaseIndex.invertedIndexMatrixIntegerEncoder import (run as encode_database_and_indexing,
                                                                    get_size_of_largest_set_of_pointers)
from Client.searchQueryIntegerEncoder import run as encode_query
from Client.fileIntegerDecoder import run as decode_retrieval

def update_mpc_script():
    with open('Server/DatabaseIndex/InvertedIndexMatrix.json', 'r') as f:
        inverted_index_matrix = load(f)
    number_of_indices = len(inverted_index_matrix.keys())

    with Path('Server/MockData/PNR Records/', mode='r') as f:
        contents = [path for path in f.rglob('*')]
    number_of_files = len(contents)

    with open('MP-SPDZ Files/MP-SPDZ_Only_Scheme.mpc', 'r') as f:
        script = f.read()

    pointer_set_size = get_size_of_largest_set_of_pointers(inverted_index_matrix)

    script = sub(r'number_of_indices = [\d]*', f'number_of_indices = {number_of_indices}', script)
    script = sub(r'number_of_files = [\d]*', f'number_of_files = {number_of_files}', script)
    script = sub(r'size_of_set_of_pointers = [\d]*', f'size_of_set_of_pointers = {pointer_set_size}', script)

    with open('MP-SPDZ Files/MP-SPDZ_Only_Scheme.mpc', 'w') as f:
        f.write(script)

if __name__ == "__main__":
    generate_data()
    #generate_indexing()
    generate_inverse_index_matrix()
    encode_database_and_indexing()
    encode_query()
    update_mpc_script()
    run(['./compile_and_run.sh'])
    # run(['./run.sh'])
    decode_retrieval()
