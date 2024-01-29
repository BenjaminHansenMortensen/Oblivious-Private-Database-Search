""" MP-SPDZ only supports a few data types, so we have to encode or data to use it. """

# Imports
from hashlib import sha256
from pathlib import Path

# Local getter imports.
from Proof_of_Concept.getters import (get_encoding_base as
                                      encoding_base)
from Proof_of_Concept.getters import (get_client_mp_spdz_input_path as
                                      mp_spdz_input_path)


def convert_search_query_to_integer(search_query: str) -> int:
    """
        Converts a search query to an integer by hashing the index then converting the digest from binary to decimals.

        Parameters:
            - search_query (str) : The search query to be converted.

        Returns:
            :raises
            - decimal_digest (int) = The index encoded as integers.
    """

    if type(search_query) is not str:
        raise TypeError('Search query is not a string.')

    binary_digest = sha256(search_query.encode('ASCII')).hexdigest()
    decimal_digest = int(binary_digest, encoding_base())

    return decimal_digest


def write_list(search_query: int, output_path: Path | str) -> None:
    """
        Writes the search queries on the correct format as the client's input into MP-SPDZ.

        Parameters:
            - search_query (int) : The search query to be written.
            - output_path (Path | str) : Client's MP-SPDZ input path.

        Returns:
            :raises
            -
    """

    try:
        output_path = Path(output_path)

    except TypeError:
        raise TypeError('Cannot covert output path to Path object')
    if type(search_query) is not int:
        raise TypeError('The search query is not encoded.')

    with output_path.open(mode='w') as f:
        f.write(str(search_query))
        f.close()


def run(search_query: str) -> None:
    """
        Encodes the search query by hashing it.

        Parameters:
            - search_query (str) : The search query.

        Returns:
            :raises
            -
    """

    encoded_search_query = convert_search_query_to_integer(search_query)

    output_path = mp_spdz_input_path().parent / f'{mp_spdz_input_path()}-P0-0'
    write_list(encoded_search_query, output_path)

    return
