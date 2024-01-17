""" Decrypts retrieved files. """

#Imports
from pathlib import Path
from json import dump
from Oblivious_Database_Query_Scheme.getters import get_number_of_blocks as number_of_blocks
from Oblivious_Database_Query_Scheme.getters import get_retrieved_records_directory as retrieved_records_directory
from Oblivious_Database_Query_Scheme.getters import get_max_file_length as max_file_length
from Oblivious_Database_Query_Scheme.getters import get_encoding_base as encoding_base
from Oblivious_Database_Query_Scheme.getters import get_block_size as block_size


def decrypt_file(ciphertexts: list[str], key_streams: list[str]) -> list[str]:
    """
        Decodes the file from ascii integers to ascii characters.

        Parameters:
            - contents (list) : The contents of the encoded file.

        Returns:
            :raises TypeError
            - files (list[dict]) : The dictionary representation of the json file.
    """

    plaintexts = []
    for i in range(number_of_blocks()):
        ciphertext = int(ciphertexts[i], 16)
        key_stream = int(key_streams[i], 16)

        plaintext = f"{(ciphertext ^ key_stream):0{32}x}"
        plaintexts.append(plaintext)

    return plaintexts


def decode_file(plaintexts: list[str]) -> dict:
    """

    """

    encoded_record = ["".join(plaintexts)[i: i + 2] for i in range(0, max_file_length() * 2, 2)]

    record = ""
    for encoded_character in encoded_record:
        ascii_value = int(encoded_character, 16)
        if ascii_value != 0 and ascii_value != 128:
            record += chr(ascii_value)

    return eval(record)


def write_file(record: dict):
    """
        Writes the json files.

        Parameters:
            - files (list[dict]) : The files to be written.
            - file_path (Path | str) : Path to the file.

        Returns:
            :raises TypeError
    """

    pnr_number = record['PNR Number']
    file_path = retrieved_records_directory() / f'record{pnr_number}.json'
    with file_path.open('w') as file:
        dump(record, file, indent=4)


def run(ciphertexts: list[list[str]], key_streams: list[list[str]]):
    """

    """
    for i in range(len(ciphertexts)):
        plaintexts = decrypt_file(ciphertexts[i], key_streams[i])
        record = decode_file(plaintexts)
        write_file(record)
