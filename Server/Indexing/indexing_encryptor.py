""" Hides the indices under a secret key. """

#Imports
from os import urandom
from json import load, dump
from hashlib import shake_128
from cryptography.hazmat.primitives.ciphers import (Cipher, algorithms, modes)
from Oblivious_Database_Query_Scheme.getters import get_inverted_index_matrix_path as inverted_index_matrix_path
from Oblivious_Database_Query_Scheme.getters import get_encrypted_inverted_index_matrix_path as encrypted_inverted_index_matrix_path
from Oblivious_Database_Query_Scheme.getters import get_block_size as block_size


def aes_128_ctr(key: bytes, nonce: bytes, plaintext: bytes) -> str:

    # Construct an AES-CTR Cipher object with the given key and a randomly generated nonce.
    encryptor = Cipher(
        algorithms.AES(key),
        modes.CTR(nonce),
    ).encryptor()

    # Encrypt the all zero plaintext and get the key stream.
    key_stream = encryptor.update(plaintext) + encryptor.finalize()

    return key_stream.hex()


def encrypt_index(index: str, encryption_key: bytes, number_of_bytes) -> str:
    """
        Converts an index to an integer by hashing the index then converting the digest from binary to decimal.

        Parameters:
            - index (str) : The index to be converted.

        Returns:
            :raises TypeError
            decimal_digest (int) = The index encoded as integers.
    """

    index_digest = shake_128(index.encode('ASCII')).digest(number_of_bytes)
    encrypted_index = aes_128_ctr(encryption_key, index_digest, index_digest)

    return encrypted_index


def encrypt_inverted_index_matrix(inverted_index_matrix: dict[str, list[str]], encryption_key: bytes, number_of_bytes: int) -> dict[str, list[str]]:
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

        encrypted_index = encrypt_index(index, encryption_key, number_of_bytes)
        encrypted_inverted_index_matrix[encrypted_index] = inverted_index_matrix[index]

    return encrypted_inverted_index_matrix


def run():
    with inverted_index_matrix_path().open('r') as file:
        inverted_index_matrix = load(file)

    number_of_bytes = block_size() // 8
    encryption_key = urandom(number_of_bytes)

    encrypted_inverted_index_matrix = encrypt_inverted_index_matrix(inverted_index_matrix, encryption_key, number_of_bytes)

    with encrypted_inverted_index_matrix_path().open('w') as file:
        dump(encrypted_inverted_index_matrix, file, indent=4)
