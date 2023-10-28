""" To build the database we want to index the records to create an inverse index martix with the indecies and full files """

#Imports
from pathlib import Path
from json import load
from hashlib import sha256


def convert_file_to_integers(contents: str) -> list[int]:
    """
        Converts each character of a file to its ascii integer encoding.

        Parameters:
            - file (dict) : The file to be converted.

        Returns:
            integer_encodings (list) = The file encoded as ascii integers.
    """

    if type(contents) != str:
        raise TypeError('Inverse index matrix is not a string.')

    contents = contents.strip().replace(' ', '').replace('\n', '')

    integer_encodings = []
    for character in contents:
        integer_encodings.append(ord(character))

    padding_amount = 6000 - len(integer_encodings)   # 6000 is the upper bound of character for the largest file.
    for i in range(padding_amount):
        integer_encodings.append(0)

    return integer_encodings


def convert_index_to_integer(index: str) -> int:
    """
        Converts an index to a integer by hashing the index then converting the digest from binary to decimals.

        Parameters:
            - index (str) : The index to be converted.

        Returns:
            decimal_digest (int) = The index encoded as integers.
    """

    if type(index) != str:
        raise TypeError('Inverse index matrix is not a string.')

    binary_digest = sha256(index.encode('ASCII')).hexdigest()
    decimal_digest = int(binary_digest, 16)

    return decimal_digest


def replace_pointers_with_file_encoded_as_integers(index_pointer_dictionary: dict, base_path: Path | str)\
        -> dict[int, list]:
    """
        Replaces each file pointer with the ascii integer encoding of the file.

        Parameters:
            - index_pointer_dictionary (dict) : The inverse index matrix dictionary with memory address pointers.

        Returns:
            integer_encoding_dictionary (dict) = The new inverse index matrix with files.
    """

    try:
        path = Path(base_path)

        if not path.is_dir() or not path.exists():
            raise NotADirectoryError
    except TypeError:
        raise TypeError('Cannot covert base path to Path object')
    if type(index_pointer_dictionary) != dict:
        raise TypeError('Inverse index matrix is not a dictionary.')
    elif all(type(value) == dict for value in index_pointer_dictionary.values()):
        raise ValueError('Dictionary is not flat.')

    integer_encoding_dictionary = {}
    for index in index_pointer_dictionary.keys():
        files = []
        for pointer in index_pointer_dictionary[index]:
            file_path = base_path / pointer
            with file_path.open(mode='r') as f:
                contents = f.read()
            integer_encoding = convert_file_to_integers(contents)

            files.append(integer_encoding)

        integer_index = convert_index_to_integer(index)
        integer_encoding_dictionary[integer_index] = files

    return integer_encoding_dictionary


def write(integer_dictionary: dict[int, list[int]], output_path: Path | str) -> None:
    """
        Writes the dictionary on the correct format as the server's input into MP-SPDZ.

        Parameters:
            - integer_dictionary (dict[int, list[int]]) : The dictionary to be written.

        Returns:

    """

    try:
        output_path = Path(output_path)

    except TypeError:
        raise TypeError('Cannot covert output path to Path object')
    if type(integer_dictionary) != dict:
        raise TypeError('Is not of type dictionary')
    elif all(type(key) != int for key in integer_dictionary.keys()):
        raise TypeError('Not all keys are integers')
    elif all(type(value) != list for value in integer_dictionary.values()):

        raise TypeError('Not all values are integers')

    output = ''
    for key in integer_dictionary.keys():
        output += f'{key} '
        for value in integer_dictionary[key]:
            for character in value:
                output += f'{character} '

    with output_path.open(mode='w') as f:
        f.write(output)


if __name__ == "__main__":
    index_path = Path('InvertedIndexMatrix.json')
    with index_path.open(mode='r') as f:
        inverted_index_matrix = load(f)

    base_path = Path('../MockData/PNR Records/')
    index_integer_dictionary = replace_pointers_with_file_encoded_as_integers(inverted_index_matrix, base_path)

    output_path = Path('../MP-SPDZ Inputs/Circuit_Only_Input-P0')
    write(index_integer_dictionary, output_path)
