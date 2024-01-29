""" MP-SPDZ only supports a few data types, so we have to encode our data to use it. """

# Imports
from pathlib import Path
from json import load
from hashlib import sha256
from re import sub

# Local getter imports.
from Proof_of_Concept.getters import (get_encoding_base as
                                      encoding_base)
from Proof_of_Concept.getters import (get_records_length_upper_bound as
                                      records_length_upper_bound)
from Proof_of_Concept.getters import (get_inverted_index_matrix_path as
                                      inverted_index_matrix_path)
from Proof_of_Concept.getters import (get_records_directory as
                                      records_directory)
from Proof_of_Concept.getters import (get_server_mp_spdz_input_path as
                                      mp_spdz_input_path)


def get_size_of_largest_set_of_pointers(inverted_index_matrix: dict[str, list[str]]) -> int:
    """
        Traverses the inverted index matrix to ind the largest set of pointers among the indices.

        Parameters:
            :raises TypeError
             - inverted_index_matrix (dict[str, list[str]]) : The inverted index matrix to be traversed.

        Returns:
            :raises
            - size_of_largest_set (int) : The size of the largest set of pointers.
    """

    if type(inverted_index_matrix) is not dict:
        raise TypeError('Is not of type dictionary.')
    elif all(type(value) is not list for value in inverted_index_matrix.values()):
        raise TypeError('Dictionary is not formatted correctly.')
    elif all(type(key) is not str for key in inverted_index_matrix.keys()):
        raise TypeError('Dictionary is not encoded as strings.')

    max_size = 1
    for pointers in inverted_index_matrix.values():
        size_of_set = len(pointers)
        if size_of_set > max_size:
            max_size = size_of_set

    return max_size


def convert_file_to_integers(contents: str) -> list[int]:
    """
        Converts each character of a file to its ascii value.

        Parameters:
            :raises TypeError
            - file (dict) : The file to be converted.

        Returns:
            :raises
            - integer_encodings (list) = The file encoded as ascii value.
    """

    if type(contents) is not str:
        raise TypeError('Inverse index matrix is not a string.')

    contents = contents.strip().replace('\n', '')
    contents = sub(r'\s+(?=([^"]*"[^"]*")*[^"]*$)', '', contents)   # Removes all whitespace outside quotes.

    integer_encodings = []
    for character in contents:
        integer_encodings.append(ord(character))

    padding_amount = records_length_upper_bound() - len(integer_encodings)
    for i in range(padding_amount):
        integer_encodings.append(0)

    return integer_encodings


def convert_string_to_unique_integer(index: str) -> int:
    """
        Converts an index to an integer by hashing the index then converting the digest from binary to decimal.

        Parameters:
            - index (str) : The index to be converted.

        Returns:
            :raises TypeError
            - decimal_digest (int) = The index encoded as integers.
    """

    if type(index) is not str:
        raise TypeError('Inverse index matrix is not a string.')

    binary_digest = sha256(index.encode('ASCII')).hexdigest()
    decimal_digest = int(binary_digest, encoding_base())

    return decimal_digest


def encode_inverted_index_matrix(inverted_index_matrix: dict[str, list[str]]) -> dict[int, list[int]]:
    """
        Encodes the indices and pointers of the inverted index matrix to integers (hashes in decimal form).

        Parameters:
            - inverted_index_matrix (dict[str, list[str]]) : The inverted index matrix to be encoded.

        Returns:
            :raises TypeError
           -  encoded_inverted_index_matrix (dict[int, list[int]]) : The encoded inverted index matrix.

    """

    if type(inverted_index_matrix) is not dict:
        raise TypeError('Is not of type dictionary.')
    elif all(type(value) is not list for value in inverted_index_matrix.values()):
        raise TypeError('Dictionary is not formatted correctly.')
    elif all(type(key) is not str for key in inverted_index_matrix.keys()):
        raise TypeError('Dictionary is not encoded as strings.')
    for pointers in inverted_index_matrix.values():
        for pointer in pointers:
            if type(pointer) is not str:
                raise TypeError('Dictionary is not encoded as strings.')

    encoded_inverted_index_matrix = {}
    size_of_largest_set_of_pointers = get_size_of_largest_set_of_pointers(inverted_index_matrix)
    for index in inverted_index_matrix.keys():

        integer_pointers = []
        for pointer in inverted_index_matrix[index]:
            integer_pointer = convert_string_to_unique_integer(pointer)
            integer_pointers.append(integer_pointer)

        padding_amount = size_of_largest_set_of_pointers - len(integer_pointers)
        for i in range(padding_amount):
            integer_pointers.append(0)

        integer_index = convert_string_to_unique_integer(index)
        encoded_inverted_index_matrix[integer_index] = integer_pointers

    return encoded_inverted_index_matrix


def get_encoded_database(index_pointer_dictionary: dict, base_path: Path | str) -> list[list[int]]:
    """
        Encodes the file hash as integers and the file contents as ascii values, on the form record1
        -> [hash, char 1, ... , char n]

        Parameters:
            - index_pointer_dictionary (dict) : The inverse index matrix dictionary with pointers.
            - base_path (Path | str) : The path to the database records.

        Returns:
            :raises TypeError
            - encoded_database (list[list[int]]) : The encoded database as integers.
    """

    try:
        base_path = Path(base_path)

    except TypeError:
        raise TypeError('Cannot covert base path to Path object.')
    if type(index_pointer_dictionary) is not dict:
        raise TypeError('Is not of type dictionary.')
    elif all(type(value) is not list for value in index_pointer_dictionary.values()):
        raise TypeError('Dictionary is not formatted correctly.')
    elif all(type(key) is not str for key in index_pointer_dictionary.keys()):
        raise TypeError('Dictionary is not encoded as string.')
    for pointers in index_pointer_dictionary.values():
        for pointer in pointers:
            if type(pointer) is not str:
                raise TypeError('Dictionary is not encoded as string.')

    visited_pointers = set()

    encoded_database = []
    for index in index_pointer_dictionary.keys():

        files = []
        for pointer in index_pointer_dictionary[index]:
            if pointer in visited_pointers:
                continue

            visited_pointers.add(pointer)

            file_path = base_path / f'record{pointer}.json'
            with file_path.open(mode='r') as f:
                contents = f.read()
                f.close()
            integer_encoding = convert_file_to_integers(contents)

            files += integer_encoding

        if len(files) == 0:
            continue

        integer_index = convert_string_to_unique_integer(pointer)
        encoded_database.append([integer_index] + files)

    return encoded_database


def write_dictionary(inverted_index_matrix: dict[int, list[int]], database: list[list[int]], output_path: Path | str):
    """
        Writes the encoded inverted index matrix and encoded database on the correct format as the server's input into
        MP-SPDZ.

        Parameters:
            - inverted_index_matrix (dict[int, list[int]]) : The encoded inverted index matrix to be written.
            - database (list[list[int]]) : The encoded database to be written.
            - output_path (Path | str) : The output where the dictionary will be written to.

        Returns:
            :raises
            -
    """

    try:
        output_path = Path(output_path)

    except TypeError:
        raise TypeError('Cannot covert output path to Path object.')
    if type(inverted_index_matrix) is not dict:
        raise TypeError('Is not of type dictionary.')
    elif all(type(value) is not list for value in inverted_index_matrix.values()):
        raise TypeError('Dictionary is not formatted correctly.')
    elif all(type(key) is not int for key in inverted_index_matrix.keys()):
        raise TypeError('Dictionary is not encoded as integers.')
    for pointers in inverted_index_matrix.values():
        for pointer in pointers:
            if type(pointer) is not int:
                raise TypeError('Dictionary is not encoded as integers.')
    if all(type(file) is not list for file in database):
        raise TypeError('The database is not encoded correctly.')
    for file in database:
        for character in file:
            if type(character) is not int:
                raise TypeError('The database is not encoded as integers.')

    output = ''
    for file in database:
        for character in file:
            output += f'{character} '

    for key in inverted_index_matrix.keys():
        output += f'{key} '
        for pointer in inverted_index_matrix[key]:
            output += f'{pointer} '

    with output_path.open(mode='w') as f:
        f.write(output)
        f.close()


def run() -> None:
    """
        Creates an inverted index matrix of the records and writes it.

        Parameters:
            -

        Returns:
            :raises
            -
    """

    with inverted_index_matrix_path().open(mode='r') as f:
        inverted_index_matrix = load(f)
        f.close()

    encoded_database = get_encoded_database(inverted_index_matrix, records_directory())
    encoded_inverted_index_matrix = encode_inverted_index_matrix(inverted_index_matrix)

    output_path = mp_spdz_input_path().parent / f'{mp_spdz_input_path().name}-P1-0'
    write_dictionary(encoded_inverted_index_matrix, encoded_database, output_path)

    return
