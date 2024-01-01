""" Encodes a record """

from pathlib import Path
from re import sub
from Oblivious_Database_Query_Scheme.run import get_encoding_base as encoding_base
from Oblivious_Database_Query_Scheme.run import get_max_file_length as max_file_length
from Oblivious_Database_Query_Scheme.run import get_block_size as block_size


def read_file(file_path: Path) -> str:
    """
        Reads the file and removes unnecessary whitespace.

        Parameters:
            - file_path (Path) : The path to the file.

        Returns:
            :raises FileNotFoundError, ValueError
            - file_content (str) = The contents of the file.
    """

    if not file_path.exists() and not file_path.is_file():
        raise FileNotFoundError(f"Did not find file at {file_path}.")
    if file_path.suffix != ".json":
        raise ValueError("File is not in the correct format.")

    with file_path.open(mode='r') as f:
        file_content = f.read()

    # Removes all whitespace outside of quotes, leaving keys and values intact.
    file_content = file_content.strip().replace('\n', '')
    file_content = sub(r'\s+(?=([^"]*"[^"]*")*[^"]*$)', '', file_content)

    return file_content


def add_padding(file: list[str]) -> list[str]:
    """
        Pads the file til desired length.

        Parameters:
            - file (list[str]) : The list with the file contents.
            - padded_length (int) : The desired total length of the file.

        Returns:
            :raises
            - file (list[str]) = The padded file.
    """

    if max_file_length() % block_size() != 0:
        raise ValueError("Padded length has to be divisible by the block size.")

    padding_amount = max_file_length() - len(file)
    for i in range(padding_amount):
        file.append("00")

    return file


def group(file: list[str]) -> list[str]:
    """
        Groups the hexadecimal encoded characters into blocks.

        Parameters:
            - file (list[str]) : List with hexadecimals.

        Returns:
            :raises
            - encode_file (list[str]) = The file grouped into blocks.
    """

    encode_file = []
    for i in range(0, len(file), encoding_base()):
        block = "0x" + "".join(file[i:i + encoding_base()])
        encode_file.append(block)

    return encode_file


def encode_file_as_hexadecimals(file_content: str) -> list[str]:
    """
        Transforms a file into a list of hexadecimal.

        Parameters:
            - file_content (str) : The file.

        Returns:
            :raises
            - encode_file (list[str]) = The file as hexadecimals.
    """

    encoded_file = []
    for character in file_content:
        encoded_file.append(f"{ord(character):0{2}x}")

    encoded_file = add_padding(encoded_file)

    return encoded_file


def encode_file(file_path: Path) -> list[str]:
    """
        Reads and makes a copy of the file which it transforms a file into blocks of hexadecimals.

        Parameters:
            - file_path (Path) : The path to the file.

        Returns:
            :raises
            - encode_file (list[str]) = The file in hexadecimal blocks.
    """

    file_content = read_file(file_path)

    encoded_file = encode_file_as_hexadecimals(file_content)

    encoded_file = group(encoded_file)

    return encoded_file
