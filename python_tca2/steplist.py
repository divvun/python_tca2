from itertools import product

from python_tca2.pathstep import PathStep

MAX_NUM_TRY = 2
MIN_NUM_TRY = 0
MAX_DIFF_TRY = 1
MAX_TOTAL_TRY = 3


def is_valid_increment(combination: tuple[int, ...]) -> bool:
    """Check if the increment combination is valid based on the constraints.

    Args:
        increment: The increment combination.
        num_files: The number of files.

    Returns:
        True if the increment combination is valid, False otherwise.
    """
    minimum, maximum, total = min(combination), max(combination), sum(combination)
    return maximum > 0 and maximum - minimum <= MAX_DIFF_TRY and total <= MAX_TOTAL_TRY


def create_step_list(num_files: int) -> list[PathStep]:
    """Create a list of PathStep objects based on the given number of files.

    Args:
        num_files: The number of files.

    Returns:
        A list of PathStep objects.
    """
    return [
        PathStep(increment_combination)
        for increment_combination in product(
            range(MIN_NUM_TRY, MAX_NUM_TRY + 1), repeat=num_files
        )
        if is_valid_increment(increment_combination)
    ]
