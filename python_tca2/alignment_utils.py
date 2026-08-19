

def count_words(string: str) -> int:
    """Counts the number of words in a given string.

    Parameters:
        string: The input string to count words from.

    Returns:
        The number of words in the input string.
    """
    return len(string.split())
