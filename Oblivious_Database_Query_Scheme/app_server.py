""" Runs the server side of the application. """

# Local getters imports.
from Oblivious_Database_Query_Scheme.getters import working_directory_validation, mp_spdz_directory_validation
from Oblivious_Database_Query_Scheme.getters import (get_encrypted_records_directory as
                                                     encrypted_pnr_records_directory)
from Oblivious_Database_Query_Scheme.getters import (get_excluded_records as
                                                     excluded_pnr_records)
from Oblivious_Database_Query_Scheme.getters import (get_records_directory as
                                                     pnr_records_directory)
from Oblivious_Database_Query_Scheme.getters import (get_server_indexing_files_directory as
                                                     server_indexing_files_directory)

# Server import.
from Oblivious_Database_Query_Scheme.Server.server import Communicator as Server


def clean_up_files() -> None:
    """
        Removes files created from previous pre-processing.

        Parameters:
            -

        Returns:
            :raises
            -
    """

    # Removes the stored encrypted PNR records.
    file_paths = [path for path in encrypted_pnr_records_directory().glob('*')]
    for file_path in file_paths:
        file_path.unlink()

    # Removes the stored PNR records.
    file_paths = [path for path in pnr_records_directory().glob('*') if (path.name not in excluded_pnr_records())]
    for file_path in file_paths:
        file_path.unlink()

    # removes the stored indexing files.
    file_paths = [path for path in server_indexing_files_directory().glob('*')]
    for file_path in file_paths:
        file_path.unlink()

    return


if __name__ == '__main__':
    # Sets the working directory and validates it and MP-SPDZ's path
    working_directory_validation()
    mp_spdz_directory_validation()

    # Starts the server and waits for the client to connect.
    server = Server()
    server.wait_for_client()

    # Executes a new pre-processing of the database.
    if not server.resume_from_previous_preprocessing:

        # Removes files from the previous pre-processing.
        clean_up_files()

        # Initializes the database with PNR records.
        server.generate_pnr_records()

        # Creates an inverted index matrix of the database.
        server.create_inverted_index_matrix()

        # Requests dummy items from the client to fill the database to the required size.
        server.request_dummy_items()

        # Encryption of the inverted index matrix.
        server.encrypt_inverted_index_matrix()

        # Waits for the client to start the records pre-processing.
        server.wait_for_records_preprocessing()

        # Sends the encrypted inverted index matrix to the client.
        server.send_encrypted_inverted_index_matrix()

    # Standby for encrypting search queries and sending encrypted records until the client goes offline.
    while server.client_online:
        server.wait_for_client_shutdown()

    # Shutdown of the server.
    server.kill()
