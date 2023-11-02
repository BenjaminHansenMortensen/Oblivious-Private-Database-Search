""" MP-SPDZ only supports a few data types, so we have to encode or data to use it. """

#Imports
from pathlib import Path
from json import load
from hashlib import sha256


def get_size_of_largest_set_of_pointers(inverted_index_matrix: dict[str, list[str]]) -> int:
    """
        Traverses the inverted index matrix to ind the largest set of pointers among the indices.

        Parameters:
            :raises TypeError
             - inverted_index_matrix (dict[str, list[str]]) : The inverted index matrix to be traversed.

        Returns:
            size_of_largest_set (int) : The size of the largest set of pointers.
    """

    if type(inverted_index_matrix) != dict:
        raise TypeError('Is not of type dictionary.')
    elif all(type(value) != list for value in inverted_index_matrix.values()):
        raise TypeError('Dictionary is not formatted correctly.')
    elif all(type(key) != str for key in inverted_index_matrix.keys()):
        raise TypeError('Dictionary is not encoded as strings.')
    for pointers in inverted_index_matrix.values():
        for pointer in pointers:
            if type(pointer) != str:
                raise TypeError('Dictionary is not encoded as strings.')

    max = 1
    for pointers in inverted_index_matrix.values():
        size_of_set = len(pointers)
        if  size_of_set > max:
            max = size_of_set

    return max


def convert_file_to_integers(contents: str) -> list[int]:
    """
        Converts each character of a file to its ascii code.

        Parameters:
            :raises TypeError
            - file (dict) : The file to be converted.

        Returns:
            integer_encodings (list) = The file encoded as ascii code.
    """

    if type(contents) != str:
        raise TypeError('Inverse index matrix is not a string.')

    contents = contents.strip().replace(' ', '').replace('\n', '')

    integer_encodings = []
    for character in contents:
        integer_encodings.append(ord(character))

    file_length_upper_bound = 6000
    padding_amount = file_length_upper_bound - len(integer_encodings)
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
            decimal_digest (int) = The index encoded as integers.
    """

    if type(index) != str:
        raise TypeError('Inverse index matrix is not a string.')

    binary_digest = sha256(index.encode('ASCII')).hexdigest()
    decimal_digest = int(binary_digest, 16)

    return decimal_digest


def encode_inverted_index_matrix(inverted_index_matrix: dict[str, list[str]]) -> dict[int, list[int]]:
    """
        Encodes the indices and pointers of the inverted index matrix to integers.

        Parameters:
            - inverted_index_matrix (dict[str, list[str]]) : The inverted index matrix to be encoded.

        Returns:
            :raises TypeError
            encoded_inverted_index_matrix (dict[int, list[int]]) : The encoded inverted index matrix.

    """

    if type(inverted_index_matrix) != dict:
        raise TypeError('Is not of type dictionary.')
    elif all(type(value) != list for value in inverted_index_matrix.values()):
        raise TypeError('Dictionary is not formatted correctly.')
    elif all(type(key) != str for key in inverted_index_matrix.keys()):
        raise TypeError('Dictionary is not encoded as strings.')
    for pointers in inverted_index_matrix.values():
        for pointer in pointers:
            if type(pointer) != str:
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
        Encodes the file hash as integers and the file contents as ascii integers, on the form record1
        -> [hash, char 1, ... , char n]

        Parameters:
            - index_pointer_dictionary (dict) : The inverse index matrix dictionary with pointers.
            - base_path (Path | str) : The path to the database files.

        Returns:
            :raises TypeError
            encoded_database (list[list[int]]) : The encoded database as integers.

    """

    try:
        base_path = Path(base_path)

    except TypeError:
        raise TypeError('Cannot covert base path to Path object.')
    if type(index_pointer_dictionary) != dict:
        raise TypeError('Is not of type dictionary.')
    elif all(type(value) != list for value in index_pointer_dictionary.values()):
        raise TypeError('Dictionary is not formatted correctly.')
    elif all(type(key) != str for key in index_pointer_dictionary.keys()):
        raise TypeError('Dictionary is not encoded as string.')
    for pointers in index_pointer_dictionary.values():
        for pointer in pointers:
            if type(pointer) != str:
                raise TypeError('Dictionary is not encoded as string.')

    visited_pointers = set()

    encoded_database = []
    for index in index_pointer_dictionary.keys():

        files = []
        for pointer in index_pointer_dictionary[index]:
            if pointer in visited_pointers:
                continue

            visited_pointers.add(pointer)

            file_path = base_path / pointer
            with file_path.open(mode='r') as f:
                contents = f.read()
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

    """

    try:
        output_path = Path(output_path)

    except TypeError:
        raise TypeError('Cannot covert output path to Path object.')
    if type(inverted_index_matrix) != dict:
        raise TypeError('Is not of type dictionary.')
    elif all(type(value) != list for value in inverted_index_matrix.values()):
        raise TypeError('Dictionary is not formatted correctly.')
    elif all(type(key) != int for key in inverted_index_matrix.keys()):
        raise TypeError('Dictionary is not encoded as integers.')
    for pointers in inverted_index_matrix.values():
        for pointer in pointers:
            if type(pointer) != int:
                raise TypeError('Dictionary is not encoded as integers.')
    if all(type(file) != list for file in database):
        raise TypeError('The database is not encoded correctly.')
    for file in database:
        for character in file:
            if type(character) != int:
                raise TypeError('The database is not encoded as integers.')

    output = ''
    for key in inverted_index_matrix.keys():
        output += f'{key} '
        for pointer in inverted_index_matrix[key]:
            output += f'{pointer} '

    for file in database:
        for character in file:
            output += f'{character} '

    with output_path.open(mode='w') as f:
        f.write(output)


def run():
    index_path = Path('Server/DatabaseIndex/InvertedIndexMatrix.json')
    with index_path.open(mode='r') as f:
        inverted_index_matrix = load(f)

    base_path = Path('Server/MockData/PNR Records/')
    encoded_database = get_encoded_database(inverted_index_matrix, base_path)
    encoded_inverted_index_matrix = encode_inverted_index_matrix(inverted_index_matrix)

    output_path = Path('Server/MP-SPDZ Inputs/MP-SPDZ_Only_Input-P1-0')
    write_dictionary(encoded_inverted_index_matrix, encoded_database, output_path)
