import inspect
import sys
from os.path import basename
from typing import Any


def print_frame(debug: str = "", *args: Any) -> None:
    """Print debug output."""
    # 0 represents this line, 1 represents line at caller
    callerframerecord = inspect.stack()[1]
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)

    print(
        basename(info.filename),
        info.lineno,
        info.function,
        debug,
        file=sys.stderr,
        end=" ",
    )
    for arg in args:
        print(arg, file=sys.stderr, end=" ")
    print(file=sys.stderr)


def overlaps(pos: int, length: int, other_pos: int, other_length: int) -> bool:
    """Determine if two ranges overlap based on their positions and lengths.

    Args:
        pos: The starting position of the first range.
        length: The length of the first range.
        other_pos: The starting position of the second range.
        other_length: The length of the second range.

    Returns:
        True if the two ranges overlap, False otherwise.
    """
    return pos <= other_pos + other_length - 1 and other_pos <= pos + length - 1


def count_words(string: str) -> int:
    """Counts the number of words in a given string.

    Parameters:
        string: The input string to count words from.

    Returns:
        The number of words in the input string.
    """
    return len(string.split())
