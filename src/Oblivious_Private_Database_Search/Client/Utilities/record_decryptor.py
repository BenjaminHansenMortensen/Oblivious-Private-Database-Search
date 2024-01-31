""" Decrypts retrieved records. """

# Imports.
from json import dump
from numpy import fromstring

# Local getters imports.
from Oblivious_Private_Database_Search.getters import (get_retrieved_records_directory as
                                                       retrieved_records_directory)
from Oblivious_Private_Database_Search.getters import (get_max_file_length as
                                                       max_file_length)


def xor(bytes_a: bytes, bytes_b: bytes) -> bytes:
    """
        XORs two bytes objects.

        Parameters:
            - bytes_a (bytes) : Bytes object to be XORed
            - bytes_b (bytes) : Bytes object to be XORed

        Returns:
            :raises
            -

    """
    bytestring_a = fromstring(bytes_a, dtype='uint8')
    bytestring_b = fromstring(bytes_b, dtype='uint8')

    return (bytestring_a ^ bytestring_b).tostring()


def decrypt_record(ciphertext: bytes, key_stream: bytes) -> bytes:
    """
        Decrypts a record.

        Parameters:
            - ciphertexts (bytes) : The encrypted record.
            - key_streams (bytes) : The decryption key streams.

        Returns:
            :raises
            - plaintexts (bytes) : The record.
    """

    # Decrypts the record.
    decrypted_record = xor(ciphertext, key_stream)

    return decrypted_record


def decode_record(encoded_record: str) -> dict:
    """
        Decodes a record by decoding every hexadecimal ascii value into a character.

        Parameters:
            - encoded_record (str) : The encoded record.
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


def run(encrypted_record: bytes, key_stream: bytes) -> None:
    """
        Writes the record.

        Parameters:
            - encrypted_record (bytes) : The encrypted record.
            - key_streams (bytes) : The corresponding decryption key streams.

        Returns:
            :raises
            -
    """

    # Decrypts and writes the record.
    encoded_record = decrypt_record(encrypted_record, key_stream)
    record = decode_record(encoded_record.hex())
    write_record(record)

    return
