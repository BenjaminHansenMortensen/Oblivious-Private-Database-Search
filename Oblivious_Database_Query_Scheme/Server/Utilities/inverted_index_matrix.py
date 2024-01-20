""" To build the database we want to index the records to create an inverse index matrix. """

# Imports
from pathlib import Path
from json import load, dump
from random import shuffle

# Local getters imports.
from Oblivious_Database_Query_Scheme.getters import (get_records_directory as
                                                     records_directory)
from Oblivious_Database_Query_Scheme.getters import (get_excluded_records as
                                                     excluded_records)
from Oblivious_Database_Query_Scheme.getters import (get_inverted_index_matrix_path as
                                                     inverted_index_matrix_path)


def read_record(record_path: str | Path) -> dict:
    """
        Reads a record file.

        Parameters:
            - path (str) : The path to the file including name.

        Returns:
            - record (dict) = The record.
    """

    # Reads the record.
    with record_path.open('r') as file:
        record = dict(load(file))

    return record


def flatten_and_filter_dictionary(dictionary: dict) -> dict:
    """
        Flattens a dictionary.

        Parameters:
            - dictionary (dict) : The dictionary to be flattened.

        Returns:
            :raises TypeError
            - flat_dictionary (dict) = The flattened dictionary.
    """

    key_filter = ['Date', 'City', 'Zip Code', 'Vendor', 'Type', 'Bonus Program', 'Airline', 'Travel Agency',
                  'Airport Name', 'City', 'Status', 'Seat', 'Cabin', 'Checked', 'Special']

    attribute_filter = {'IATA Code': ['AES', 'ALF', 'ANX', 'BDU', 'BJF', 'BJF', 'BGO', 'BVG', 'BOO', 'BNN', 'VDB',
                                      'FAN', 'FRO', 'FDE', 'DLD', 'GLL', 'HMR', 'HFT', 'EVE', 'HAA', 'HAU', 'HVG',
                                      'QKX', 'KKN', 'KRS', 'KSU', 'LKL', 'LKN', 'MEH', 'MQN', 'MOL', 'MJF', 'RYG',
                                      'OSY', 'NVK', 'NTB', 'OLA', 'HOV', 'FBU', 'OSL', 'RRS', 'RVK', 'RET', 'SDN',
                                      'TRF', 'SSJ', 'SKE', 'SOG', 'SOJ', 'SVG', 'SKN', 'SRP', 'LYR', 'SVJ', 'TOS',
                                      'TRD', 'VDS', 'VRY', 'VAW']}

    flat_dictionary = {}

    # Adds and filters the keys and values of the dictionary.
    add_keys_and_values(flat_dictionary, dictionary, key_filter, attribute_filter)

    return flat_dictionary


def add_keys_and_values(flat_dictionary: dict, dictionary: dict, key_filter: list,
                        attribute_filter: dict, parent_key: str = '') -> None:
    """
    Add keys and values to the flattened dictionary. Iterates through child dictionaries.

    Parameters:
        - flat_dictionary (dict) : The dictionary where keys and values are added it.
        - dictionary (dict) : The dictionary to be flattened.
        - key_filter (list) : A list of values to filter out unwanted information.
        - parent_key (str) : The key of the parent dictionary.

    Returns:
        -
    """

    # Filters and adds keys and values to the flatten dictionary.
    for key, value in dictionary.items():
        # Filtering of keys and values.
        if key in key_filter:
            continue
        elif key in attribute_filter:
            if value in attribute_filter[key]:
                continue

        # Recursively flattens the dictionary.
        if type(value) is dict:
            if parent_key != '':
                key = f'{parent_key} {key}'

            add_keys_and_values(flat_dictionary, value, key_filter, attribute_filter, key)
        else:
            flat_dictionary[f'{parent_key} {key}'] = value

    return


def update_inverse_index_matrix(inverse_index_matrix: dict, record: dict[str, str], index: str) -> None:
    """
        Updates the inverse index matrix with the contents of a record.

        Parameters:
            - record (dict[str, str]) : The flattened record.
            - dictionary (dict) : The memory location of the record.

        Returns:
            -
    """

    # Adds the attributes of a record as keys to the inverted index matrix and updates that attribute's with the
    # record's index.
    for key, value in record.items():
        if value in list(inverse_index_matrix.keys()):
            indices = inverse_index_matrix[value]
            if index not in indices:
                indices.append(index)
        else:
            inverse_index_matrix[value] = [index]

    return


def run() -> list[Path]:
    """
        Creates an inverted index matrix of the records.

        Parameters:
            -

        Returns:
            - record_pointers (list[Path]) : The pointers to the records.
    """

    # Creates a list of pointers of the records and shuffles them.
    records_path = [path for path in records_directory().glob('*') if (path.name not in excluded_records())]
    shuffle(records_path)

    # Creates an inverse index matrix of the records.
    inverse_index_matrix = {}
    for pointer in range(len(records_path)):
        record_path = records_path[pointer]
        if record_path.suffix != ".json":
            continue
        record = read_record(record_path)
        record = flatten_and_filter_dictionary(record)
        update_inverse_index_matrix(inverse_index_matrix, record, str(pointer))

    # Writes the inverted index matrix to the indexing directory.
    with inverted_index_matrix_path().open('w') as file:
        dump(inverse_index_matrix, file, indent=4)

    record_pointers = records_path

    return record_pointers
