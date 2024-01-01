""" The getters for the different variables used by the Oblivious Database Query Scheme """

from pathlib import Path
from os import chdir


def working_directory_validation() -> Path:
    """
        Validates the path to the Oblivious Database Query directory.

        Parameters:
            -

        Returns:
            :raises Exception, NotADirectoryError
            - working_directory (Path) : The path to where the application will work from.
    """

    working_directory = Path.cwd().parent

    try:
        chdir(working_directory)
    except Exception:
        print("Could not set a new working directory.")

    return working_directory


def MP_SPDZ_directory_validation() -> Path:
    """
        Validates the path to the MP-SPDZ directory.

        Parameters:
            -

        Returns:
            :raises Exception, NotADirectoryError
            - MP_SPDZ_directory (Path) : The path to the MP-SPDZ directory.
    """

    MP_SPDZ_directory = Path.cwd().parent.parent.parent / "MP-SPDZ"

    if not MP_SPDZ_directory.is_dir() or not MP_SPDZ_directory.exists():
        raise NotADirectoryError("The MP-SPDZ path is not valid.")

    return MP_SPDZ_directory


def get_encoding_base() -> int:
    """ Getter for the encoding_base variable """
    encoding_base = 16
    return encoding_base


def get_max_file_length() -> int:
    """ Getter for the max_file_length variable """
    max_file_length = 6016
    return max_file_length


def get_number_of_blocks() -> int:
    """ Getter for the number_of_blocks variable """
    number_of_blocks = get_max_file_length() // get_encoding_base()
    return number_of_blocks


def get_database_size() -> int:
    """ Getter for the database_size variable """
    database_size = 2**4
    return database_size


def get_MP_SPDZ_directory() -> Path:
    """ Getter for the MP_SPDZ_directory variable """
    MP_SPDZ_directory = MP_SPDZ_directory_validation()
    return MP_SPDZ_directory


def get_working_directory() -> Path:
    """ Getter for the working_directory variable """
    working_directory = working_directory_validation()
    return working_directory


def get_block_size() -> int:
    """ Getter for the block_size variable """
    block_size = 128
    return block_size