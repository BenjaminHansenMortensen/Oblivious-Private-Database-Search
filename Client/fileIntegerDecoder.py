""" Transforms the retrieved file from the MP-SPDZ only scheme to a legitimate json file. """

#Imports
from pathlib import Path
from json import load, dump

def read_file(file_path: Path | str) -> str:
    """
        Reads the integer encoded file.

        Parameters:
            - file_path (Path | str) : Path to the file.

        Returns:
            :raises TypeError
            - contents (list) : The contents of the file.
    """

    try:
        file_path = Path(file_path)
        if not file_path.is_file() or not file_path.exists():
            raise ValueError('File path does not lead to a file.')
    except TypeError:
        raise TypeError('Cannot covert output path to Path object')

    with file_path.open(mode='r') as f:
        contents = load(f)

    return contents

def decode_file(contents: list[int]) -> list[str]:
    """
        Decodes the file from ascii integers to ascii characters.

        Parameters:
            - contents (list) : The contents of the encoded file.

        Returns:
            :raises TypeError
            - decoded_file (list[str]) : The string representation of the .json file.
    """

    if type(contents) != list:
        raise TypeError('Is not of type list.')
    elif all(type(value) != int for value in contents):
        raise TypeError('Contents is not ascii value encoded.')

    decoded_contents = []
    for ascii_value in contents:
        if ascii_value == 0:
            continue

        decoded_contents.append(chr(ascii_value))

    return decoded_contents

def write_file(contents: list[str], output_path: Path | str):
    """
        Writes the string as json file.

        Parameters:
            - file_path (Path | str) : Path to the file.

        Returns:
            :raises TypeError
    """

    try:
        output_path = Path(output_path)

        if not output_path.is_dir() or not output_path.exists():
            raise ValueError('Directory does not exist.')
    except TypeError:
        raise TypeError('Cannot covert output path to Path object')
    if type(contents) != list:
        raise TypeError('Is not of type list.')
    elif all(type(value) != str for value in contents):
        raise TypeError('Contents is not ascii characters encoded.')

    files = []
    start = 0
    open_close = 0
    for i in range(len(contents)):
        match contents[i]:
            case '{':
                open_close += 1
            case'}':
                open_close -= 1

        if contents[i] == '}' and open_close == 0:
            file = eval(''.join(contents[start : i + 1]))
            files.append(file)
            start = i

    for i in range(len(files)):
        file = files[i]
        file_path = output_path / f'record{i + 1}'
        with file_path.open('w') as fp:
            dump(file, fp, indent=4)


if __name__ == "__main__":
    file_path = Path('MP-SPDZ Outputs/MP-SPDZ_Only_Output-P0-0')
    contents = read_file(file_path)
    decoded_contents = decode_file(contents)
    output_path = Path('Retrieved Records/')
    write_file(decoded_contents, output_path)

