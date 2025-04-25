"""This module provides functionality for generating alignment suggestions."""

from itertools import product

AlignmentSuggestion = tuple[int, ...]
"""A type alias for a tuple of integers representing an alignment suggestion.

This tuple contains the number of AlignmentElement objects to be added from
each text to an alignment tuple (:py:type:`AlignedSentenceElements`).

For example, an AlignmentSuggestion of (1, 2) means that one AlignmentElement
object should be added from the first text and two AlignmentElement objects
should be added from the second text.
"""
MAX_DIFF_TRY = 1
"""int: The maximum allowed difference between the largest and smallest values in an 
alignment suggestion.
"""
MAX_TOTAL_TRY = 3
"""int: The maximum allowed sum of values in an alignment suggestion."""


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
"""int: The maximum value for each element in an alignment suggestion."""
MIN_NUM_TRY = 0
"""int: The minimum value for each element in an alignment suggestion."""


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
