""" Generates a key stream. """

# Imports
from os import urandom
from cryptography.hazmat.primitives.ciphers import (Cipher, algorithms, modes)

# Local getters imports.
from Oblivious_Database_Query_Scheme.getters import (get_number_of_blocks as
                                                     number_of_blocks)
from Oblivious_Database_Query_Scheme.getters import (get_block_size as
                                                     block_size)


def aes_128_ctr(key: bytes, plaintext: bytes, number_of_bytes: int) -> str:
    """
        Generates a new key stream by encrypting a nonce under some key using AES-128bit in CTR mode, then xor it with
        an all zero bit plaintext.

        Parameters:
            - record (dict) : The record to be written.

        Returns:
            :raises
            - key_stream (str) : New key stream.
    """

    # Generate a random 128-bit nonce.
    nonce = urandom(number_of_bytes)

    # Construct an AES-CTR Cipher object with the given key and a randomly generated nonce.
    encryptor = Cipher(
        algorithms.AES(key),
        modes.CTR(nonce),
    ).encryptor()

    # Encrypt the all zero plaintext and get the key stream.
    key_stream = encryptor.update(plaintext) + encryptor.finalize()

    return key_stream.hex()


def get_key_streams() -> list[str]:
    """
        Gets key streams to encrypt a record.

        Parameters:
            -

        Returns:
            :raises
            - key_streams (list[str]) : The encryption key streams.
    """

    number_of_bytes = block_size() // 8

    zero_plaintext = bytearray(number_of_bytes)

    # Collects enough key streams to encrypt a record.
    key_streams = []
    for _ in range(number_of_blocks()):
        key = urandom(number_of_bytes)
        key_stream = aes_128_ctr(key, zero_plaintext, number_of_bytes)
        key_streams.append(key_stream)

    return key_streams
