""" Runs the oblivious data query scheme """

from Oblivious_Database_Query_Scheme.getters import working_directory_validation, MP_SPDZ_directory_validation
from Oblivious_Database_Query_Scheme.Server.server import Communicator as Server


def clean_up_files():
    """

    """

    from Oblivious_Database_Query_Scheme.getters import get_encrypted_PNR_records_directory as encrypted_PNR_records_directory
    file_paths = [path for path in encrypted_PNR_records_directory().glob('*')]
    for file_path in file_paths:
        file_path.unlink()

    from Oblivious_Database_Query_Scheme.getters import get_excluded_PNR_records as excluded_PNR_records
    from Oblivious_Database_Query_Scheme.getters import get_PNR_records_directory as PNR_records_directory
    file_paths = [path for path in PNR_records_directory().glob('*') if (path.name not in excluded_PNR_records())]
    for file_path in file_paths:
        file_path.unlink()

    from Oblivious_Database_Query_Scheme.getters import get_server_indexing_files_directory as server_indexing_files_directory
    file_paths = [path for path in server_indexing_files_directory().glob('*')]
    for file_path in file_paths:
        file_path.unlink()


if __name__ == '__main__':
    # Sets the working directory and validates it and MP-SPDZ's path
    working_directory_validation()
    MP_SPDZ_directory_validation()

    server = Server()
    server.wait_for_client()

    if not server.resume_from_previous:
        clean_up_files()

        # Initializes the database with PNR records
        server.create_database()

        # Creates an inverted index matrix of the database
        server.create_indexing()

        server.request_dummy_items()

        # Ephemeral encryption of the indexing
        server.encrypt_indexing()

        server.wait_for_preprocessing()

        server.send_encrypted_indexing()

    # Searching and file retrieval
    while server.client_online:
        server.wait_for_client_shutdown()

    server.kill()
