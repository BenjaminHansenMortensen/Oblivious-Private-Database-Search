""" To build the database we want to index the records to create an inverse index martix """

#Imports
from pathlib import Path
from json import load, dump


def read_record(path: str | Path) -> dict:
    """
        Reads a record file.

        Parameters:
            - path (str) : The path to the file including name.

        Returns:
            record (dict) = The record.
    """
    try:
        path = Path(path)

        if not path.is_file() or path.suffix != '.json':
            raise ValueError('Did not find .json file')
    except TypeError:
        raise TypeError(f'Cannot covert to Path object')


    with open(path, 'r') as file:
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

    if type(dictionary) != dict:
        raise TypeError('The dictionary is not of type dictionary.')

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
        elif type(value) == dict:
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

    """

    if type(record) != dict:
        raise TypeError(' Record is not a dictionary.')
    elif all(type(value) == dict for value in record.values()):
        raise ValueError('Dictionary is not flat.')
    # TODO Memory Location Error Handling

    memory_location = memory_location.name

    indexing[memory_location] = [value for value in record.values()]


def get_contents(path: str | Path) -> list[str]:
    """
        Gets the contents of a directory.

        Parameters:
            - path (str | Path) : The path to the directory.

        Returns:
            :raises: NotADirectoryError, TypeError
            contents (list[str]) : All the contents of the directory.

    """

    try:
        dir = Path(path)

        if not dir.is_dir() or not dir.exists():
            raise NotADirectoryError
    except TypeError:
        raise TypeError('Cannot covert directory to Path object')


    contents = [path for path in dir.rglob('*')]

    return contents


def run():
    indexing = {}
    path = 'Server/MockData/PNR Records/'
    files = get_contents(path)
    for file in files:
        record = read_record(file)
        record = flatten_and_filter_dictionary(record)
        update_index(indexing, record, file)

    with open(f'Server/DatabaseIndex/Indexing.json', 'w') as fp:
        dump(indexing, fp, indent=4)
