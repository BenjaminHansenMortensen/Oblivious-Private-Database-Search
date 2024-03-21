""" To build the database we want to index the records to create a semantic indexing. """

# Imports
from pathlib import Path
from json import load, dump
from numpy import multiply
from sentence_transformers import SentenceTransformer
from warnings import simplefilter

# Local getter imports.
from application.getters import (get_server_semantic_indexing_path as
                                 server_semantic_indexing_path)
from application.getters import (get_embedding_model as
                                 embedding_model)
from application.getters import (get_float_to_integer_scalar as
                                 float_to_integer_scalar)

# Warning filtering.
simplefilter('ignore', UserWarning)


def read_record(record_path: Path) -> dict:
    """
        Reads a record.

        Parameters:
            - record_path (Path) : The path to the record.

        Returns:
            :raises
            - record (dict) = The record.
    """

    with record_path.open('r') as f:
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

    key_filter = []

    attribute_filter = {}

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
        - attribute_filter (dict) : A list of values to filter out unwanted information.
        - parent_key (str) : The key of the parent dictionary.

    Returns:
        :raises
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


def update_index(model: SentenceTransformer, indexing: dict, record: dict[str, str], pointer: int) -> None:
    """
        Updates the keywords (index) and locations of a record to the index matrix.

        Parameters:
            - model (SentenceTransformer) : The text embedding model.
            - indexing (dict) : Dictionary to be updated with the indexing.
            - record (dict[str, str]) : The flattened record.
            - pointer (int) : The memory location of the record.

        Returns:
            :raises
            -

    """

    # Gets the embedding of the record. (Requires internet connection)
    record_embedding = model.encode(f'{record}')

    # Scaled embedding.
    scaled_record_embedding = multiply(record_embedding, float_to_integer_scalar()).astype(int).tolist()

    # Adds the semantic record embedding to the indexing.
    indexing[pointer] = scaled_record_embedding

    return


def run(record_pointers: list[Path]) -> None:
    """
        Creates a semantic indexing of the records.

        Parameters:
            - record_pointers (list[Path]) : The pointers to the records.

        Returns:
            :raises
            -
    """

    # Text embedding model.
    model = SentenceTransformer(embedding_model())

    indexing = {}
    for pointer in range(len(record_pointers)):
        record_path = record_pointers[pointer]
        record = read_record(record_path)
        record = flatten_and_filter_dictionary(record)
        update_index(model, indexing, record, pointer)

    # Writes the semantic indexing to the indexing directory.
    with server_semantic_indexing_path().open('w') as f:
        dump(indexing, f, indent=4)
        f.close()

    return
