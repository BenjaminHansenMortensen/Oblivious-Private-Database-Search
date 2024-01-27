""" Hides the inverted index matrix attributes under a secret key. """

# Imports
from os import urandom
from json import load, dump
from hashlib import shake_128
from random import shuffle
from cryptography.hazmat.primitives.ciphers import (Cipher, algorithms, modes)

# Local getters imports.
from Oblivious_Database_Query_Scheme.getters import (get_inverted_index_matrix_path as
                                                     inverted_index_matrix_path)
from Oblivious_Database_Query_Scheme.getters import (get_server_encrypted_inverted_index_matrix_directory as
                                                     encrypted_inverted_index_matrix_directory)
from Oblivious_Database_Query_Scheme.getters import (get_number_of_bytes as
                                                     number_of_bytes)
from Oblivious_Database_Query_Scheme.getters import (get_max_amount_of_attributes_per_record as
                                                     max_amount_of_attributes_per_record)
from Oblivious_Database_Query_Scheme.getters import (get_encrypted_inverted_index_matrix_attribute_limit as
                                                     encrypted_inverted_index_matrix_attribute_limit)


def aes_128_ecb(key: bytes, plaintext: bytes) -> str:
    """
        AES-128bit in ECB mode.

        Parameters:
            - key (bytes) : The encryption key.
            - plaintext (bytes) : The plaintext to be encrypted.

        Returns:
            :raises
            - ciphertext (str) : The ciphertext as a hexadecimal.
    """

    # Construct an AES-ECB Cipher object with the given key.
    encryptor = Cipher(
        algorithms.AES(key),
        modes.ECB(),
    ).encryptor()

    # Encrypts the plaintext with the key.
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    return ciphertext.hex()


def encrypt_attribute(attribute: str, encryption_key: bytes) -> str:
    """
        Encrypts an attribute by hashing it and encrypting it as the plaintext input to a block cipher.

        Parameters:
            - attribute (str) : The attribute to be encrypted.

        Returns:
            :raises
            - encrypted_attribute (str) = The encrypted attribute.
    """

    # Hashes the
    attribute_digest = shake_128(attribute.encode('ASCII')).digest(number_of_bytes())
    encrypted_attribute = aes_128_ecb(encryption_key, attribute_digest)

    return encrypted_attribute


def get_number_of_attributes_per_record(inverted_index_matrix: dict[str, list[str]]) -> dict[str, int]:
    """
        Finds the number of attributes per record.
        
        Parameters:
            - inverted_index_matrix (dict[str, list[str]]) : The inverted index matrix.
            
        Returns:
            :raises
            - frequencies (dict[str, int]) : The number of attributes per record.
    """

    frequencies = {}
    
    for indices in inverted_index_matrix.values():
        for index in indices:
            if index in frequencies:
                frequencies[index] += 1
            else:
                frequencies[index] = 0
    
    return frequencies


def encrypt_and_pad_inverted_index_matrix(inverted_index_matrix: dict[str, list[str]],
                                          encryption_key: bytes) -> dict[str, list[str]]:
    """
        Encrypts the attributes (dictionary keys) of the inverted index matrix, and pads it so that every record index
        has the same amount of attributes.

        Parameters:
            - inverted_index_matrix (dict[str, list[str]]) : The inverted index matrix to be encoded.

        Returns:
            :raises
            - encrypted_inverted_index_matrix (dict[int, list[int]]) : The encrypted inverted index matrix.

    """

    # Encrypts the attributes of the inverse index matrix.
    encrypted_inverted_index_matrix = {}
    for attribute in inverted_index_matrix.keys():

        encrypted_attribute = encrypt_attribute(attribute, encryption_key)
        encrypted_inverted_index_matrix[encrypted_attribute] = inverted_index_matrix[attribute]

    attributes_per_index = get_number_of_attributes_per_record(inverted_index_matrix)

    # Adds padding so that every record index is referenced the same amount of times.
    for record_index in attributes_per_index.keys():
        for i in range(max_amount_of_attributes_per_record() - attributes_per_index[record_index]):
            dummy_attribute = urandom(number_of_bytes())
            encrypted_dummy_attribute = aes_128_ecb(encryption_key, dummy_attribute)
            encrypted_inverted_index_matrix[encrypted_dummy_attribute] = [record_index]

    return encrypted_inverted_index_matrix


def shuffle_dictionary(encrypted_inverted_index_matrix: dict[str, list[str]]) -> dict[str, list[str]]:
    """
        Shuffles the encrypted inverted index matrix.

        Parameters:
            - encrypted_inverted_index_matrix (dict) : The dictionary to be shuffled.

        Returns:
            :raises
            - shuffles_encrypted_inverted_index_matrix (dict) : The shuffled dictionary.
    """

    encrypted_inverted_index_matrix_keys = list(encrypted_inverted_index_matrix.keys())
    shuffle(encrypted_inverted_index_matrix_keys)
    shuffled_encrypted_inverted_index_matrix = {}
    for key in encrypted_inverted_index_matrix_keys:
        shuffled_encrypted_inverted_index_matrix[key] = encrypted_inverted_index_matrix[key]

    return shuffled_encrypted_inverted_index_matrix


def write_encrypted_inverted_index_matrix(encrypted_inverted_index_matrix: dict[str, list[str]]) -> None:
    """
        Writes the encrypted inverted index matrix to multiple files depending on its length.

        Parameters:
            - encrypted_inverted_index_matrix (dict) : The dictionary to be written.

        Returns:
            :raises
            -
    """

    temp_dictionary = {}
    counter = 0
    file_counter = 0
    for attribute in encrypted_inverted_index_matrix.keys():
        temp_dictionary[attribute] = encrypted_inverted_index_matrix[attribute]
        counter += 1

        if counter == encrypted_inverted_index_matrix_attribute_limit():
            # Writes part of the encrypted inverted index matrix.
            with open(encrypted_inverted_index_matrix_directory() /
                      f'Encrypted_Inverted_Index_Matrix{file_counter}.json', 'w') as f:
                dump(temp_dictionary, f, indent=4)
                f.close()

            file_counter += 1
            temp_dictionary = {}
            counter = 0

    # Writes the remaining part of the encrypted inverted index matrix.
    with open(encrypted_inverted_index_matrix_directory() /
              f'Encrypted_Inverted_Index_Matrix{file_counter}.json', 'w') as f:
        dump(temp_dictionary, f, indent=4)
        f.close()

    return


def run() -> str:
    """
        Encrypts the attributes of the inverted index matrix.

        Parameters:
            -

        Returns:
            :raises
            - encryption_key (str) = The encryption key as hexadecimal.
    """

    # reads the inverted index matrix.
    with inverted_index_matrix_path().open('r') as file:
        inverted_index_matrix = load(file)

    # Gets a new encryption key.
    encryption_key = urandom(number_of_bytes())

    # Encrypts and pads the inverted index matrix.
    encrypted_inverted_index_matrix = encrypt_and_pad_inverted_index_matrix(inverted_index_matrix, encryption_key)

    # Shuffles the encrypted inverted index matrix.
    encrypted_inverted_index_matrix = shuffle_dictionary(encrypted_inverted_index_matrix)

    # Writes the encrypted inverted index matrix.
    write_encrypted_inverted_index_matrix(encrypted_inverted_index_matrix)

    return encryption_key.hex()
