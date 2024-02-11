""" Transforms the retrieved file from the MP-SPDZ only scheme to a legitimate json file. """

# Imports
from pathlib import Path
from json import load, dump

# Local getter imports.
from Proof_of_Concept.getters import (get_retrieved_records_directory as
                                      retrieved_records_path)
from Proof_of_Concept.getters import (get_client_mp_spdz_output_path as
                                      mp_spdz_output_path)


def read_file(file_path: Path | str) -> list[list[int]]:
    """
        Reads the integer encoded file.

        Parameters:
            - file_path (Path | str) : Path to the file.

        Returns:
            :raises TypeError
            - contents (list[list[int]]) : The contents of the file.
    """

    try:
        file_path = Path(file_path)
        if not file_path.is_file() or not file_path.exists():
            raise ValueError('File path does not lead to a file.')
    except TypeError:
        raise TypeError('Cannot covert output path to Path object')

    with file_path.open(mode='r') as f:
        contents = eval(f.read())
        f.close()

    return contents


def decode_file(contents: list[int]) -> list[dict]:
    """
        Decodes the file from ascii integers to ascii characters.

        Parameters:
            - contents (list[int]) : The contents of the encoded file.

        Returns:
            :raises TypeError
            - records (list[dict]) : The dictionary representation of the json file.
    """

    if type(contents) is not list:
        raise TypeError('Is not of type list.')
    elif all(type(value) is not int for value in contents):
        raise TypeError('Contents is not ascii value encoded.')

    decoded_contents = []
    for ascii_value in contents:
        if ascii_value == 0:
            continue

        decoded_contents.append(chr(ascii_value))

    files = []
    start = 0
    open_close = 0
    for i in range(len(decoded_contents)):
        match decoded_contents[i]:
            case '{':
                open_close += 1
            case'}':
                open_close -= 1

        if decoded_contents[i] == '}' and open_close == 0:
            file = eval(''.join(decoded_contents[start: i + 1]))
            files.append(file)
            start = i + 1

    return files


def write_file(records: list[dict], output_path: Path | str) -> None:
    """
        Writes the json records.

        Parameters:
            - records (list[dict]) : The records to be written.
            - file_path (Path | str) : Path to the record.

        Returns:
            :raises TypeError
            -
    """

    try:
        output_path = Path(output_path)

        if not output_path.is_dir() or not output_path.exists():
            raise ValueError('Directory does not exist.')
    except TypeError:
        raise TypeError('Cannot covert output path to Path object')
    if type(records) is not list:
        raise TypeError('Is not of type list.')
    elif all(type(file) is not dict for file in records):
        if len(records) == 0:
            return
        raise TypeError('Not all values are decoded records.')

    for i in range(len(records)):
        record = records[i]
        pnr_number = record['PNR Number']
        file_path = output_path / f'record{pnr_number}.json'
        with file_path.open('w') as f:
            dump(record, f, indent=4)
            f.close()

    return


def run() -> None:
    """
        Decodes the record from the MP-SPDZ output file.

        Parameters:
            -

        Returns:
            :raises
            -
    """

    encoded_record_path = mp_spdz_output_path().parent / f'{mp_spdz_output_path().name}-P0-0'
    contents = read_file(encoded_record_path)
    for content in contents:
        file = decode_file(content)
        write_file(file, retrieved_records_path())

    return
