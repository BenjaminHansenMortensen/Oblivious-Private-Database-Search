""" Runs the oblivious data query scheme """

from Oblivious_Database_Query_Scheme.getters import working_directory_validation, get_database_size
from Server.Data_Generation.generatePNR_Data import run as create_database
from Client.Preprocessing.bitonic_sort import bitonic_sort as permute_and_encrypt_database

if __name__ == '__main__':
    # Sets the working directory
    working_directory_validation()

    # Initializes the database
    create_database(get_database_size())

    # Preprocesses the indexing and AES key_streams

    # Creates a new secret database
    #indexing = permute_and_encrypt_database(database_size, working_directory, MP_SPDZ_directory)

