""" Runs the oblivious data query scheme """

from pathlib import Path
from os import chdir
from Server.MockData.generatePNR_Data import run as create_database


def directory_validation() -> tuple[Path, Path]:
    """
        Validates the path to the MP-SPDZ directory and the Oblivious Database Query directory.

        Parameters:
            -

        Returns:
            - MP_SPDZ_directory (Path) : The path to the MP-SPDZ directory.
            - working_directory (Path) : The path to where the application will work from.
    """

    MP_SPDZ_directory = Path.cwd().parent.parent.parent / "MP-SPDZ"
    working_directory = Path.cwd().parent

    try:
        chdir(working_directory)
    except Exception:
        print("Could not set a new working directory.")

    if not MP_SPDZ_directory.is_dir() or not MP_SPDZ_directory.exists():
        raise NotADirectoryError("The MP-SPDZ path is not valid.")

    return MP_SPDZ_directory, working_directory


if __name__ == '__main__':
    MP_SPDZ_directory, working_directory = directory_validation()

    # Initialize the database
    database_size = 2**4
    create_database(database_size)

