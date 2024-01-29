""" To build the database we want to index the records. """

# Imports
from pathlib import Path
from json import load, dump

# Local getter imports.
from Proof_of_Concept.getters import (get_excluded_records as
                                      excluded_records)
from Proof_of_Concept.getters import (get_records_directory as
                                      records_directory)
from Proof_of_Concept.getters import (get_indexing_path as
                                      indexing_path)


def read_record(path: str | Path) -> dict:
    """
        Reads a record file.

        Parameters:
            - path (str) : The path to the file including name.

        Returns:
            :raises
            - record (dict) = The record.
    """
    try:
        path = Path(path)

        if not path.is_file() or path.suffix != '.json':
            raise ValueError('Did not find .json file')
    except TypeError:
        raise TypeError(f'Cannot covert to Path object')

    with path.open('r') as f:
        record = dict(load(f))
        f.close()

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

    if type(dictionary) is not dict:
        raise TypeError('The provided dictionary is not of type dictionary.')

    key_filter = ['Date', 'City', 'Zip Code', 'Vendor', 'Type', 'Bonus Program', 'Airline', 'Travel Agency',
                  'IATA Code', 'Airport Name', 'City', 'Status', 'Seat', 'Cabin', 'Checked', 'Special']

    flat_dictionary = {}

    add_keys_and_values(flat_dictionary, dictionary, key_filter)

    return flat_dictionary


def add_keys_and_values(flat_dictionary: dict, dictionary: dict, key_filter: list, parent_key: str = ''):
    """
    Add keys and values to the flattened dictionary. Iterates through child dictionaries.

    Parameters:
        - flat_dictionary (dict) : The dictionary where keys and values are added it.
        - dictionary (dict) : The dictionary to be flattened.
        - key_filter (list) : A list of values to filter out unwanted information.
        - parent_key (str) : The key of the parent dictionary.

    Returns:
        :raises
        -
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


def update_index(indexing: dict, record: dict[str, str], memory_location: str | Path):
    """
        Updates the keywords (index) and locations of a record to the index matrix.

        Parameters:
            - record (dict[str, str]) : The flattened record.
            - dictionary (dict) : The memory location of the record.

        Returns:
            :raises
            -
    """

    if type(record) is not dict:
        raise TypeError(' Record is not a dictionary.')
    elif all(type(value) is dict for value in record.values()):
        raise ValueError('Dictionary is not flat.')

    memory_location = memory_location.name

    values = set()
    for value in record.values():
        values.add(value)

    if memory_location in indexing.keys():
        existing_values = indexing[memory_location]
        for value in existing_values:
            values.add(value)

    indexing[memory_location] = list(values)


def get_contents(path: str | Path) -> list[str | Path]:
    """
        Gets the contents of a directory.

        Parameters:
            - path (str | Path) : The path to the directory.

        Returns:
            :raises: NotADirectoryError, TypeError
            - contents (list[str]) : All the contents of the directory.
    """

    try:
        directory = Path(path)

        if not directory.is_dir() or not directory.exists():
            raise NotADirectoryError
    except TypeError:
        raise TypeError('Cannot covert directory to Path object')

    contents = [path for path in directory.rglob('*') if path.name not in excluded_records()]

    return contents


def run() -> None:
    """
        Creates an indexing of records and writes it.

        Parameters:
            -

        Returns:
            :raises
            -
    """

    indexing = {}
    record_paths = get_contents(records_directory())
    for record_path in record_paths:
        record = read_record(record_path)
        record = flatten_and_filter_dictionary(record)
        update_index(indexing, record, record_path)

    with indexing_path().open('w') as f:
        dump(indexing, f, indent=4)
        f.close()

    return
