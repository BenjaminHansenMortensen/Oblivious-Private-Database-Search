""" Decrypts retrieved files. """

# Imports.
from json import dump

# Local getters imports.
from Oblivious_Database_Query_Scheme.getters import (get_number_of_blocks as
                                                     number_of_blocks)
from Oblivious_Database_Query_Scheme.getters import (get_retrieved_records_directory as
                                                     retrieved_records_directory)
from Oblivious_Database_Query_Scheme.getters import (get_max_file_length as
                                                     max_file_length)


def decrypt_record(ciphertexts: list[str], key_streams: list[str]) -> list[str]:
    """
        Decrypts a record.

        Parameters:
            - ciphertexts (list[str]) : The encrypted record.
            - key_streams (list[str]) : The decryption key streams.

        Returns:
            :raises
            - plaintexts (list[str]) : The record.
    """

    # Decrypts the record.
    decrypted_record = []
    for i in range(number_of_blocks()):
        ciphertext = int(ciphertexts[i], 16)
        key_stream = int(key_streams[i], 16)

        plaintext = f'{(ciphertext ^ key_stream):0{32}x}'
        decrypted_record.append(plaintext)

    return decrypted_record


def decode_record(encoded_record: list[str]) -> dict:
    """
        Decodes a record by decoding every hexadecimal ascii value into a character.

        Parameters:
            - encoded_record (list[str]) : The encoded record.
        Returns:
            :raises
            - record (dict) : The record.
    """

    # Encoded record.
    encoded_record = [''.join(encoded_record)[i: i + 2] for i in range(0, max_file_length() * 2, 2)]

    # Decodes hexadecimal ascii values to characters.
    record = ''
    for encoded_character in encoded_record:
        ascii_value = int(encoded_character, 16)
        if ascii_value != 0 and ascii_value != 128:
            record += chr(ascii_value)

    record = eval(record)

    return record


def write_record(record: dict) -> None:
    """
        Writes the record.

        Parameters:
            - record (dict) : The record to be written.

        Returns:
            :raises
            -
    """

    # Writes the record.
    pnr_number = record['PNR Number']
    record_path = retrieved_records_directory() / f'record{pnr_number}.json'
    with record_path.open('w') as f:
        dump(record, f, indent=4)

    return


def run(encrypted_record: list[list[str]], key_streams: list[list[str]]) -> None:
    """
        Writes the record.

        Parameters:
            - encrypted_record (list[list[str]]) : The encrypted record.
            - key_streams (list[list[str]]) : The corresponding decryption key streams.

        Returns:
            :raises
            -
    """

    # Decrypts and writes the record.
    for i in range(len(encrypted_record)):
        encoded_record = decrypt_record(encrypted_record[i], key_streams[i])
        record = decode_record(encoded_record)
        write_record(record)

    return
