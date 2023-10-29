""" MP-SPDZ only supports a few data types, so we have to encode or data to use it. """

#Imports
from hashlib import sha256
from pathlib import Path


def convert_search_query_to_integer(search_query: str) -> int:
    """
        Converts a search query to an integer by hashing the index then converting the digest from binary to decimals.

        Parameters:
            - search_query (str) : The search query to be converted.

        Returns:
            decimal_digest (int) = The index encoded as integers.
    """

    if type(search_query) != str:
        raise TypeError('Search query is not a string.')

    binary_digest = sha256(search_query.encode('ASCII')).hexdigest()
    decimal_digest = int(binary_digest, 16)

    return decimal_digest


def convert_search_queries_to_integers(search_queries: list[str]) -> list[int]:
    """
        Converts search queries to a list of integer by hashing the index then converting the digest from binary to
        decimals.

        Parameters:
            - search_queries (list[str]) : The list of search queries to be converted.

        Returns:
            integer_encodings (list[int]) = The search queries encoded as integers.
    """

    integer_encodings = []
    for search_query in search_queries:
        integer_encoding = convert_search_query_to_integer(search_query)
        integer_encodings.append(integer_encoding)

    return integer_encodings

def write_list(search_queries: list[int], output_path: Path | str) -> None:
    """
        Writes the search queries on the correct format as the client's input into MP-SPDZ.

        Parameters:
            - integer_dictionary (dict[int, list[int]]) : The dictionary to be written.

        Returns:

    """

    try:
        output_path = Path(output_path)

    except TypeError:
        raise TypeError('Cannot covert output path to Path object')
    if type(search_queries) != list:
        raise TypeError('Is not of type dictionary')
    elif all(type(value) != int for value in search_queries):
        raise TypeError('Not all keys are integers')

    output = ''
    for search_query in search_queries:
        output += f'{search_query} '


    with output_path.open(mode='w') as f:
        f.write(output)


if __name__ == "__main__":
    search_query = ['1']
    integer_search_query = convert_search_queries_to_integers(search_query)

    output_path = Path('MP-SPDZ Inputs/Circuit_Only_Input-P0-0-0')
    write_list(integer_search_query, output_path)
