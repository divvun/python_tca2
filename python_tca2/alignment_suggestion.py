"""
This module provides functionality for generating alignment suggestions based on
constraints and validating those suggestions.

Constants:
    AlignmentSuggestion:
        A type alias for a tuple of integers representing an alignment suggestion.

    MAX_DIFF_TRY:
        The maximum allowed difference between the largest and smallest values
        in an alignment suggestion.

    MAX_TOTAL_TRY:
        The maximum allowed sum of values in an alignment suggestion.

    MAX_NUM_TRY:
        The maximum value for each element in an alignment suggestion.

    MIN_NUM_TRY:
        The minimum value for each element in an alignment suggestion.
"""

from itertools import product

AlignmentSuggestion = tuple[int, ...]
MAX_DIFF_TRY = 1
MAX_TOTAL_TRY = 3


def is_valid_suggestion(combination: tuple[int, ...]) -> bool:
    """Check if the increment combination is valid based on the constraints.

    Args:
        combination: The suggestion combination.

    Returns:
        True if the suggestion combination is valid, False otherwise.
    """
    minimum, maximum, total = min(combination), max(combination), sum(combination)
    return maximum > 0 and maximum - minimum <= MAX_DIFF_TRY and total <= MAX_TOTAL_TRY


MAX_NUM_TRY = 2
MIN_NUM_TRY = 0


def generate_alignment_suggestions(num_files: int) -> list[AlignmentSuggestion]:
    """Create a list of AlignmentSuggestions based on the given number of files.

    Args:
        num_files: The number of files.

    Returns:
        A list of AlignmentSuggestions.
    """
    return [
        AlignmentSuggestion(alignment_combination)
        for alignment_combination in product(
            range(MIN_NUM_TRY, MAX_NUM_TRY + 1), repeat=num_files
        )
        if is_valid_suggestion(alignment_combination)
    ]
