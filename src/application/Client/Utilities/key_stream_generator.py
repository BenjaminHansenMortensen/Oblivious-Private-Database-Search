""" Generates a key stream. """

# Imports
from os import urandom
from cryptography.hazmat.primitives.ciphers import (Cipher, algorithms, modes)

# Local getters imports.
from application.getters import (get_number_of_blocks as
                                 number_of_blocks)
from application.getters import (get_number_of_bytes as
                                 number_of_bytes)
from application.getters import (get_hex_block_size as
                                 hex_block_size)


def aes_128_ctr(key: bytes, plaintext: bytes, nonce: bytes) -> list[str]:
    """
        Generates a new key stream by encrypting a nonce under some key using AES-128bit in CTR mode, then xor it with
        an all zero bit ciphertext.

        Parameters:
            - key (bytes) : Encryption key.
            - ciphertext (bytes) : Plaintext to be encrypted.
            - nonce (bytes) : Number used once.

        Returns:
            :raises
            - key_streams (list[str]) : New key stream.
    """

    # Construct an AES-CTR Cipher object with the given key and a randomly generated nonce.
    encryptor = Cipher(
        algorithms.AES(key),
        modes.CTR(nonce),
    ).encryptor()    # Collects enough key streams to encrypt a record.

    # Encrypt the all zero ciphertext and get the key stream.
    key_stream = (encryptor.update(plaintext) + encryptor.finalize()).hex()

    key_streams = []
    for i in range(0, hex_block_size() * number_of_blocks(), hex_block_size()):
        block = key_stream[i: i + hex_block_size()]
        key_streams.append(block)

    return key_streams


def get_key_stream() -> tuple[list[str], str, str]:
    """
        Gets key streams to encrypt a record.

        Parameters:
            -

        Returns:
            :raises
            - key_streams (list[str]) : The encryption key stream.
            - key (str) : Encryption key.
            - nonce (str) : Number used once.
    """

    zero_plaintext = bytearray(number_of_bytes() * number_of_blocks())
    key = urandom(number_of_bytes())
    nonce = urandom(number_of_bytes())
    key_stream = aes_128_ctr(key, zero_plaintext, nonce)

    return key_stream, key.hex(), nonce.hex()
