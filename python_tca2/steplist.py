from python_tca2.pathstep import PathStep

MAX_NUM_TRY = 2
MIN_NUM_TRY = 0
MAX_DIFF_TRY = 1
MAX_TOTAL_TRY = 3


def int_to_base(number: int, base: int) -> str:
    """
    Converts an integer to a string representation in the given base.

    Args:
        number (int): The integer to be converted.
        base (int): The base to convert the integer to.

    Returns:
        str: The string representation of the integer in the given base.
    """
    if number == 0:
        return "0"

    digits = []
    while number:
        digits.append(int(number % base))
        number //= base
    digits = digits[::-1]

    return "".join(map(str, digits))


def create_step_list(num_files: int) -> list[PathStep]:
    """
    Create a list of PathStep objects based on the given number of files.

    Args:
        num_files (int): The number of files.

    Returns:
        list[PathStep]: A list of PathStep objects.
    """
    step_list: list[PathStep] = []
    range_val = MAX_NUM_TRY - MIN_NUM_TRY + 1
    limit = 1
    for _ in range(num_files):
        limit *= range_val

    for i in range(limit):
        increment = [0] * num_files

        comb_string = int_to_base(limit + i, range_val)[1 : num_files + 1]
        minimum = MAX_NUM_TRY + 1
        maximum = MIN_NUM_TRY - 1
        total = 0

        for text_number in range(num_files):
            increment[text_number] = MIN_NUM_TRY + int(
                comb_string[text_number], range_val
            )
            total += increment[text_number]
            minimum = min(minimum, increment[text_number])
            maximum = max(maximum, increment[text_number])

        if maximum > 0 and maximum - minimum <= MAX_DIFF_TRY and total <= MAX_TOTAL_TRY:
            step_list.append(PathStep(increment))

    return step_list
