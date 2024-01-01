""" Generates a key stream """

from os import urandom
from cryptography.hazmat.primitives.ciphers import (Cipher, algorithms, modes)
from Oblivious_Database_Query_Scheme.getters import get_number_of_blocks as number_of_blocks


def aes_128_ctr(key: bytes, plaintext: bytes) -> str:
    # Generate a random 128-bit nonce.
    nonce = urandom(16)

    # Construct an AES-CTR Cipher object with the given key and a randomly generated nonce.
    encryptor = Cipher(
        algorithms.AES(key),
        modes.CTR(nonce),
    ).encryptor()

    # Encrypt the all zero plaintext and get the key stream.
    key_stream = encryptor.update(plaintext) + encryptor.finalize()

    return key_stream.hex()


def get_key_streams() -> list[str]:
    zero_plaintext = bytearray(16)

    key_streams = []
    for _ in range(number_of_blocks()):
        key = urandom(16)
        key_stream = aes_128_ctr(key, zero_plaintext)
        key_streams.append(key_stream)

    return key_streams
