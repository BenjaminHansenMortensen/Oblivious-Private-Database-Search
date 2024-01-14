""" Hides the indices under a secret key. """

#Imports
from os import urandom
from json import load, dump
from hashlib import shake_128
from cryptography.hazmat.primitives.ciphers import (Cipher, algorithms, modes)
from Oblivious_Database_Query_Scheme.getters import get_inverted_index_matrix_path as inverted_index_matrix_path
from Oblivious_Database_Query_Scheme.getters import get_server_encrypted_inverted_index_matrix_path as encrypted_inverted_index_matrix_path
from Oblivious_Database_Query_Scheme.getters import get_number_of_bytes as number_of_bytes


def aes_128(key: bytes, plaintext: bytes) -> str:

    # Construct an AES-CTR Cipher object with the given key and a randomly generated nonce.
    encryptor = Cipher(
        algorithms.AES(key),
        modes.ECB(),
    ).encryptor()

    # Encrypt the all zero plaintext and get the key stream.
    key_stream = encryptor.update(plaintext) + encryptor.finalize()

    return key_stream.hex()


def encrypt_index(index: str, encryption_key: bytes) -> str:
    """
        Converts an index to an integer by hashing the index then converting the digest from binary to decimal.

        Parameters:
            - index (str) : The index to be converted.

        Returns:
            :raises TypeError
            decimal_digest (int) = The index encoded as integers.
    """

    index_digest = shake_128(index.encode('ASCII')).digest(number_of_bytes())
    encrypted_index = aes_128(encryption_key, index_digest)

    return encrypted_index


def encrypt_inverted_index_matrix(inverted_index_matrix: dict[str, list[str]], encryption_key: bytes) -> dict[str, list[str]]:
    """
        Encodes the indices and pointers of the inverted index matrix to integers (hashes in decimal form).

        Parameters:
            - inverted_index_matrix (dict[str, list[str]]) : The inverted index matrix to be encoded.

        Returns:
            :raises TypeError
            encrypted_inverted_index_matrix (dict[int, list[int]]) : The encoded inverted index matrix.

    """

    encrypted_inverted_index_matrix = {}
    for index in inverted_index_matrix.keys():

        encrypted_index = encrypt_index(index, encryption_key)
        encrypted_inverted_index_matrix[encrypted_index] = inverted_index_matrix[index]

    return encrypted_inverted_index_matrix


def run() -> str:
    with inverted_index_matrix_path().open('r') as file:
        inverted_index_matrix = load(file)

    encryption_key = urandom(number_of_bytes())

    encrypted_inverted_index_matrix = encrypt_inverted_index_matrix(inverted_index_matrix, encryption_key)

    with encrypted_inverted_index_matrix_path().open('w') as file:
        dump(encrypted_inverted_index_matrix, file, indent=4)

    return encryption_key.hex()
