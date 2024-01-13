""" To build the database we want to index the records to create an inverse index martix """

#Imports
from pathlib import Path
from json import load, dump
from Oblivious_Database_Query_Scheme.getters import get_PNR_records_directory as PNR_records_directory
from Oblivious_Database_Query_Scheme.getters import get_excluded_PNR_records as excluded_PNR_records
from Oblivious_Database_Query_Scheme.getters import get_inverted_index_matrix_path as inverted_index_matrix_path


def read_record(record_path: str | Path) -> dict:
    """
        Reads a record file.

        Parameters:
            - path (str) : The path to the file including name.

        Returns:
            record (dict) = The record.
    """

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
            flat_dictionary (dict) = The flattened dictionary.
    """

    key_filter = ['Date', 'City', 'Zip Code', 'Vendor', 'Type', 'Bonus Program', 'Airline', 'Travel Agency',
                  'IATA Code', 'Airport Name', 'City', 'Status', 'Seat', 'Cabin', 'Checked', 'Special']

    flat_dictionary = {}

    add_keys_and_values(flat_dictionary, dictionary, key_filter)

    return flat_dictionary


def add_keys_and_values(flat_dictionary: dict, dictionary: dict, key_filter: list, parent_key: str = '') -> dict:
    """
    Add keys and values to the flattened dictionary. Iterates through child dictionaries.

    Parameters:
        - flat_dictionary (dict) : The dictionary where keys and values are added it.
        - dictionary (dict) : The dictionary to be flattened.
        - key_filter (list) : A list of values to filter out unwanted information.
        - parent_key (str) : The key of the parent dictionary.

    Returns:

    """

    for key, value in dictionary.items():
        if key in key_filter:
            continue
        elif type(value) is dict:
            if parent_key != '':
                key = f'{parent_key} {key}'

            add_keys_and_values(flat_dictionary, value, key_filter, key)
        else:
            flat_dictionary[f'{parent_key} {key}'] = value


def update_inverse_index_matrix(inverse_index_matrix: dict, record: dict[str, str], pointer: int):
    """
        Updates the keywords (index) and locations of a record to the inverse index matrix.

        Parameters:
            - record (dict[str, str]) : The flattened record.
            - dictionary (dict) : The memory location of the record.

        Returns:

    """

    for key, value in record.items():
        if value in list(inverse_index_matrix.keys()):
            pointers = inverse_index_matrix[value]
            if pointer not in pointers:
                pointers.append(str(pointer))
        else:
            inverse_index_matrix[value] = [str(pointer)]


def run():
    inverse_index_matrix = {}
    records_path = [path for path in PNR_records_directory().glob('*') if path.name not in excluded_PNR_records()]

    for pointer in range(len(records_path)):
        record = read_record(records_path[pointer])
        record = flatten_and_filter_dictionary(record)
        update_inverse_index_matrix(inverse_index_matrix, record, pointer)

    with inverted_index_matrix_path().open('w') as file:
        dump(inverse_index_matrix, file, indent=4)
