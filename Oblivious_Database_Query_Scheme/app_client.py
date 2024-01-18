""" Runs the oblivious data query scheme """

from Oblivious_Database_Query_Scheme.getters import working_directory_validation, MP_SPDZ_directory_validation
from Oblivious_Database_Query_Scheme.Client.client import Communicator as Client


def clean_up_files():
    """

    """

    from Oblivious_Database_Query_Scheme.getters import get_client_indexing_directory as client_indexing_directory
    file_paths = [path for path in client_indexing_directory().glob('*')]
    for file_path in file_paths:
        file_path.unlink()

    from Oblivious_Database_Query_Scheme.getters import get_records_encryption_key_streams_directory as records_encryption_key_streams_directory
    file_paths = [path for path in records_encryption_key_streams_directory().glob('*')]
    for file_path in file_paths:
        file_path.unlink()

    from Oblivious_Database_Query_Scheme.getters import get_retrieved_records_directory as retrieved_records_directory
    file_paths = [path for path in retrieved_records_directory().glob('*')]
    for file_path in file_paths:
        file_path.unlink()


if __name__ == '__main__':
    # Sets the working directory and validates it and MP-SPDZ's path
    working_directory_validation()
    MP_SPDZ_directory_validation()

    resume = input("Resume from previous pre-processing? (y/n): ")

    client = Client()
    if resume == 'y':
        client.resume_from_previous = True
    else:
        client.resume_from_previous = False

    client.wait_for_server()

    if not client.resume_from_previous:
        clean_up_files()

        client.wait_for_encrypted_indexing()

        # Creates a new secret database
        client.send_database_preprocessing_message()

    # Searching and file retrieval
    while True:
        # Take search query from the client
        search_query = input("Search Query: ")
        if search_query == "exit":
            break

        # Encrypted the search query under the server's encryption key
        client.send_encrypt_query_message(search_query)

        # Searches and retrieves the records
        client.request_PNR_records()

    client.kill()
