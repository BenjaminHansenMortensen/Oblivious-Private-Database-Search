""" Runs the client side of the application. """

# Local getters imports.
from Oblivious_Database_Query_Scheme.getters import working_directory_validation, mp_spdz_directory_validation
from Oblivious_Database_Query_Scheme.getters import (get_client_indexing_directory as
                                                     client_indexing_directory)
from Oblivious_Database_Query_Scheme.getters import (get_records_encryption_key_streams_directory as
                                                     records_encryption_key_streams_directory)
from Oblivious_Database_Query_Scheme.getters import (get_retrieved_records_directory as
                                                     retrieved_records_directory)

# Client imports.
from Oblivious_Database_Query_Scheme.Client.client import Communicator as Client


def clean_up_files() -> None:
    """
        Removes files created from previous pre-processing.

        Parameters:
            -

        Returns:
            :raises
            -
    """

    # Removes the stored indexing files.
    file_paths = [path for path in client_indexing_directory().glob('*')]
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


if __name__ == '__main__':
    # Sets the working directory and validates it and MP-SPDZ's path.
    working_directory_validation()
    mp_spdz_directory_validation()

    # Resume from previous pre-processing input from the user.
    resume = input("Resume from previous pre-processing? (y/n): ")

    # Starts the client
    client = Client()

    # Updates local variable of the client depending on answer from the input.
    if resume == 'y':
        client.resume_from_previous_preprocessing = True
    else:
        client.resume_from_previous_preprocessing = False

    # Waits for the server to connect.
    client.wait_for_server()

    # Executes a new pre-processing of the database.
    if not client.resume_from_previous_preprocessing:

        # Removes files from the previous pre-processing.
        clean_up_files()

        # Waits for the server to request dummy items then sends them.
        client.waiting_to_send_dummy_items()

        # Shuffles and encrypts the server's records.
        client.send_records_preprocessing_message()

        # Waits for the server to send the inverted index matrix.
        client.wait_for_encrypted_inverted_index_matrix()

    # Executes searches and retrievals of the server's records.
    while True:
        # Takes a search query from the user.
        search_query = input("Search Query: ")
        if search_query == "exit":
            break

        # Encrypted the search query under the server's encryption key.
        client.send_encrypt_query_message(search_query)

        # Searches and retrieves the records. Given no results dummy items will be requested instead.
        client.request_pnr_records()

    # Shutdown of the client.
    client.kill()
