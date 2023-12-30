import inspect
import sys
from os.path import basename


def print_frame(debug="", *args):
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


def overlaps(pos, length, other_pos, other_length):
    print_frame()
    return pos <= other_pos + other_length - 1 and other_pos <= pos + length - 1


def count_words(string):
    print_frame()
    return len(string.split())
