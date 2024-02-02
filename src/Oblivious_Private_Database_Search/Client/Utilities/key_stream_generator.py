""" Generates a key stream. """

# Imports
from os import urandom
from cryptography.hazmat.primitives.ciphers import (Cipher, algorithms, modes)

# Local getters imports.
from Oblivious_Private_Database_Search.getters import (get_number_of_blocks as
                                                       number_of_blocks)
from Oblivious_Private_Database_Search.getters import (get_number_of_bytes as
                                                       number_of_bytes)


def aes_128_ctr(key: bytes, plaintext: bytes, nonce: bytes) -> bytes:
    """
        Generates a new key stream by encrypting a nonce under some key using AES-128bit in CTR mode, then xor it with
        an all zero bit plaintext.

        Parameters:
            - key (bytes) : Encryption key.
            - plaintext (bytes) : Plaintext to be encrypted.
            - nonce (bytes) : Number used once.

        Returns:
            :raises
            - key_streams (bytes) : New key stream.
    """

    # Construct an AES-CTR Cipher object with the given key and a randomly generated nonce.
    encryptor = Cipher(
        algorithms.AES(key),
        modes.CTR(nonce),
    ).encryptor()    # Collects enough key streams to encrypt a record.

    # Encrypt the all zero plaintext and get the key stream.
    key_stream = (encryptor.update(plaintext) + encryptor.finalize())

    return key_stream


def get_key_stream() -> tuple[bytes, bytes, bytes]:
    """
        Gets key streams to encrypt a record.

        Parameters:
            -

        Returns:
            :raises
            - key_streams (bytes) : The encryption key stream.
            - key (bytes) : Encryption key.
            - nonce (bytes) : Number used once.
    """

    zero_plaintext = bytearray(number_of_bytes() * number_of_blocks())
    key = urandom(number_of_bytes())
    nonce = urandom(number_of_bytes())
    key_stream = aes_128_ctr(key, zero_plaintext, nonce)

    return key_stream, key, nonce
