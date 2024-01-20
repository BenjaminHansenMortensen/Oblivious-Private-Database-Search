""" Hides the inverted index matrix attributes under a secret key. """

# Imports
from os import urandom
from json import load, dump
from hashlib import shake_128
from cryptography.hazmat.primitives.ciphers import (Cipher, algorithms, modes)

# Local getters imports.
from Oblivious_Database_Query_Scheme.getters import (get_inverted_index_matrix_path as
                                                     inverted_index_matrix_path)
from Oblivious_Database_Query_Scheme.getters import (get_server_encrypted_inverted_index_matrix_path as
                                                     encrypted_inverted_index_matrix_path)
from Oblivious_Database_Query_Scheme.getters import (get_number_of_bytes as
                                                     number_of_bytes)


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


def encrypt_inverted_index_matrix(inverted_index_matrix: dict[str, list[str]],
                                  encryption_key: bytes) -> dict[str, list[str]]:
    """
        Encrypts the attributes (dictionary keys) of the inverted index matrix.

        Parameters:
            - inverted_index_matrix (dict[str, list[str]]) : The inverted index matrix to be encoded.

        Returns:
            :raises
            - encrypted_inverted_index_matrix (dict[int, list[int]]) : The encoded inverted index matrix.

    """

    # Encrypts the attributes of the inverse index matrix.
    encrypted_inverted_index_matrix = {}
    for attribute in inverted_index_matrix.keys():

        encrypted_attribute = encrypt_attribute(attribute, encryption_key)
        encrypted_inverted_index_matrix[encrypted_attribute] = inverted_index_matrix[attribute]

    return encrypted_inverted_index_matrix


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

    # Encrypts the inverted index matrix.
    encrypted_inverted_index_matrix = encrypt_inverted_index_matrix(inverted_index_matrix, encryption_key)

    # writes the encrypted inverted index matrix.
    with encrypted_inverted_index_matrix_path().open('w') as file:
        dump(encrypted_inverted_index_matrix, file, indent=4)

    return encryption_key.hex()
