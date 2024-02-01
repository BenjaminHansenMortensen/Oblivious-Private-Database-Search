""" Runs the client side of the application. """

# Local getters imports.
from Oblivious_Private_Database_Search.getters import working_directory_validation, mp_spdz_directory_validation
from Oblivious_Private_Database_Search.getters import (get_client_indexing_directory as
                                                       client_indexing_directory)
from Oblivious_Private_Database_Search.getters import (get_records_encryption_key_streams_directory as
                                                       records_encryption_key_streams_directory)
from Oblivious_Private_Database_Search.getters import (get_retrieved_records_directory as
                                                       retrieved_records_directory)

# Client imports.
from Oblivious_Private_Database_Search.Client.client import Communicator as Client


def clean_up_files() -> None:
    """
        Removes records created from previous pre-processing.

        Parameters:
            -

        Returns:
            :raises
            -
    """

    # Removes the stored indexing records.
    file_paths = [path for path in client_indexing_directory().rglob('*') if path.is_file()]
    for file_path in file_paths:
        file_path.unlink()

    # Removes the stored encryption key streams.
    file_paths = [path for path in records_encryption_key_streams_directory().glob('*')]
    for file_path in file_paths:
        file_path.unlink()

    # Removes the stored retrieved indices.
    file_paths = [path for path in retrieved_records_directory().glob('*')]
    for file_path in file_paths:
        file_path.unlink()

    return


def main() -> None:
    # Sets the working directory and validates it and MP-SPDZ's path.
    working_directory_validation()
    mp_spdz_directory_validation()

    # Perform a semantic search input from the user.
    semantic_search_response = input("Perform a sematic search? (y/n): ")

    # Resume from previous pre-processing input from the user.
    resume_response = input("Resume from previous pre-processing? (y/n): ")

    # Starts the client
    client = Client()

    client.user_response(semantic_search_response, resume_response)

    if not client.resume_from_previous_preprocessing:

        # Removes records from the previous pre-processing.
        clean_up_files()

    # Waits for the server to connect.
    client.wait_for_server()

    # Executes a new pre-processing of the database.
    if not client.resume_from_previous_preprocessing:

        # Waits for the server to request dummy items then sends them.
        client.waiting_to_send_dummy_items()

        # Shuffles and encrypts the server's records.
        client.send_records_preprocessing_message()

        if not client.is_semantic_search:
            # Waits for the server to send the inverted index matrix.
            client.wait_for_encrypted_inverted_index_matrix()

    # Executes searching and retrievals of the server's records.
    while True:

        # Takes a search query from the user.
        search_query = input("Search Query: ")
        if search_query == "exit":
            break

        if client.is_semantic_search:
            # Semantic search
            client.send_semantic_search_message(search_query)
        else:
            # Encrypted the search query under the server's encryption key.
            client.send_encrypt_query_message(search_query)

        # Searches and retrieves the records. Given no results dummy items will be requested instead.
        client.request_records()

    # Shutdown of the client.
    client.kill()

    return


main()
