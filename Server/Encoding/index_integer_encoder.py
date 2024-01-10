""" MP-SPDZ only supports a few data types, so we have to encode our data to use it. """

#Imports
from pathlib import Path
from json import load
from Server.Encoding.inverted_index_matrix_integer_encoder import (get_size_of_largest_set_of_pointers,
                                                                   convert_file_to_integers,
                                                                   convert_string_to_unique_integer)


def get_encoded_database(indexing: dict, base_path: Path | str) -> list[list[int]]:
    """
        Encodes the file hash as integers and the file contents as ascii values, on the form record1
        -> [hash, char 1, ... , char n]

        Parameters:
            - indexing (dict) : The indexing consisting of files with attributes.
            - base_path (Path | str) : The path to the database files.

        Returns:
            :raises TypeError
            encoded_database (list[list[int]]) : The encoded database as integers.

    """

    try:
        base_path = Path(base_path)

    except TypeError:
        raise TypeError('Cannot covert base path to Path object.')
    if type(indexing) != dict:
        raise TypeError('Is not of type dictionary.')
    elif all(type(value) != list for value in indexing.values()):
        raise TypeError('Dictionary is not formatted correctly.')
    elif all(type(key) != str for key in indexing.keys()):
        raise TypeError('Dictionary is not encoded as string.')

    encoded_database = []
    for file in indexing.keys():

        file_path = base_path / file
        with file_path.open(mode='r') as f:
            contents = f.read()
        integer_encoding = convert_file_to_integers(contents)

        integer_index = convert_string_to_unique_integer(file)
        encoded_database.append([integer_index] + integer_encoding)

    return encoded_database


def encode_indexing(indexing: dict[str, list]) -> dict[int, list[int]]:
    """
        Encodes the indices and attributes as hashes in decimal form.

        Parameters:
            - indexing (dict) : The indexing consisting of files with attributes.

        Returns:
            :raises TypeError
            encoded_indexing (dict[int, list[int]]) : The encoded database as integers.

    """

    if type(indexing) != dict:
        raise TypeError('Is not of type dictionary.')
    elif all(type(value) != list for value in indexing.values()):
        raise TypeError('Dictionary is not formatted correctly.')
    elif all(type(key) != str for key in indexing.keys()):
        raise TypeError('Dictionary is not encoded as string.')

    encoded_indexing = {}
    size_of_largest_set_of_attributes = get_size_of_largest_set_of_pointers(indexing)
    for index in indexing.keys():
        encoded_attributes = []
        for attribute in indexing[index]:
            if type(attribute) != str:
                attribute = f'{attribute}'

            encoded_attribute = convert_string_to_unique_integer(attribute)
            encoded_attributes.append(encoded_attribute)

        padding_amount = size_of_largest_set_of_attributes - len(encoded_attributes)
        for i in range(padding_amount):
            encoded_attributes.append(0)

        encoded_index = convert_string_to_unique_integer(index)
        encoded_indexing[encoded_index] = encoded_attributes

    return encoded_indexing


def write_dictionary(indexing: dict[int, list[int]], database: list[list[int]], output_path: Path | str):
    """
        Writes the encoded indexing and encoded database on the correct format as the server's input into
        MP-SPDZ.

        Parameters:
            - indexing (dict[int, list[int]]) : The encoded indexing to be written.
            - database (list[list[int]]) : The encoded database to be written.
            - output_path (Path | str) : The output where the dictionary will be written to.

        Returns:

    """

    try:
        output_path = Path(output_path)

    except TypeError:
        raise TypeError('Cannot covert output path to Path object.')
    if type(indexing) != dict:
        raise TypeError('Is not of type dictionary.')
    elif all(type(value) != list for value in indexing.values()):
        raise TypeError('Dictionary is not formatted correctly.')
    elif all(type(key) != int for key in indexing.keys()):
        raise TypeError('Dictionary is not encoded as integers.')
    for pointers in indexing.values():
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
    for file in database:
        for character in file:
            output += f'{character} '

    for key in indexing.keys():
        output += f'{key} '
        for pointer in indexing[key]:
            output += f'{pointer} '

    with output_path.open(mode='w') as f:
        f.write(output)


def run():
    index_path = Path('Server/Indexing/Index_Files/Indexing.json')
    with index_path.open(mode='r') as f:
        indexing = load(f)

    base_path = Path('Server/PNR_Records/')
    encoded_database = get_encoded_database(indexing, base_path)
    encoded_indexing = encode_indexing(indexing)

    output_path = Path('Server/MP_SPDZ_Inputs/MP_SPDZ_Only_Input-P1-0')
    write_dictionary(encoded_indexing, encoded_database, output_path)
