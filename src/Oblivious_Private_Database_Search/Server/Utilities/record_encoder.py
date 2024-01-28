""" Encodes a record. """

# Imports.
from pathlib import Path
from re import sub

# Local getters imports.
from Oblivious_Private_Database_Search.getters import get_encoding_base as encoding_base
from Oblivious_Private_Database_Search.getters import get_max_file_length as max_file_length
from Oblivious_Private_Database_Search.getters import get_block_size as block_size


def read_record(record_path: Path) -> str:
    """
        Reads the record and removes unnecessary whitespace.

        Parameters:
            - record_path (Path) : The path to the record.

        Returns:
            :raises
            - record_content (str) = The contents of the record.
    """

    # Reads the record.
    with record_path.open(mode='r') as f:
        record_content = f.read()
        f.close()

    # Removes all whitespace outside of quotes, leaving keys and values intact.
    record_content = record_content.strip().replace('\n', '')
    record_content = sub(r'\s+(?=([^"]*"[^"]*")*[^"]*$)', '', record_content)

    return record_content


def add_padding(record: list[str]) -> list[str]:
    """
        Pads the record til desired length.

        Parameters:
            - record (list[str]) : The list with the record contents.
            - padded_length (int) : The desired total length of the record.

        Returns:
            :raises
            - record (list[str]) = The padded file.
    """

    if max_file_length() % block_size() != 0:
        raise ValueError('Padded length has to be divisible by the block size.')

    # Pads the record.
    padding_amount = max_file_length() - len(record)
    for i in range(padding_amount):
        record.append('00')

    return record


def group(record: list[str]) -> list[str]:
    """
        Groups the hexadecimal encoded characters into blocks.

        Parameters:
            - record (list[str]) : List with hexadecimals.

        Returns:
            :raises
            - encode_record (list[str]) = The record grouped into blocks.
    """

    # Groups the record into blocks.
    encoded_record = []
    for i in range(0, len(record), encoding_base()):
        block = ''.join(record[i:i + encoding_base()])
        encoded_record.append(block)

    return encoded_record


def encode_record_as_hexadecimals(record_content: str) -> list[str]:
    """
        Transforms a record into a list of hexadecimal by turning every character into its ascii hexadecimal value.

        Parameters:
            - record_content (str) : The record.

        Returns:
            :raises
            - encode_record (list[str]) = The record as hexadecimals.
    """

    # Encodes each character of the record into hexadecimal ascii values.
    encoded_record = []
    for character in record_content:
        encoded_record.append(f'{ord(character):0{2}x}')

    encoded_record = add_padding(encoded_record)

    return encoded_record


def encode_record(record_path: Path) -> list[str]:
    """
        Reads and makes a copy of the record which it transforms into blocks of hexadecimals.

        Parameters:
            - record_path (Path) : The path to the record.

        Returns:
            :raises
            - encode_record (list[str]) = The record in hexadecimal blocks.
    """

    # Reads the record.
    record_content = read_record(record_path)
    
    # Encodes the record.
    encoded_record = encode_record_as_hexadecimals(record_content)
    
    # Formats the encoded record.
    encoded_record = group(encoded_record)

    return encoded_record
