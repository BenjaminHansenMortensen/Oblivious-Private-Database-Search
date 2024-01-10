""" Generates a key stream """

from os import urandom
from cryptography.hazmat.primitives.ciphers import (Cipher, algorithms, modes)
from Oblivious_Database_Query_Scheme.getters import get_number_of_blocks as number_of_blocks
from Oblivious_Database_Query_Scheme.getters import get_block_size as block_size

def aes_128_ctr(key: bytes, plaintext: bytes, number_of_bytes: int) -> str:
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
    number_of_bytes = block_size() // 8

    zero_plaintext = bytearray(number_of_bytes)

    key_streams = []
    for _ in range(number_of_blocks()):
        key = urandom(number_of_bytes)
        key_stream = aes_128_ctr(key, zero_plaintext, number_of_bytes)
        key_streams.append(key_stream)

    return key_streams
