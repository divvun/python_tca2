import re

from python_tca2 import constants


def string_to_bigram(word: str) -> list[str]:
    """Convert a string into a list of bigrams (two-character sequences).

    Args:
        word: The input string to convert.
    Returns:
        A list of bigrams extracted from the input string.
    """
    lower_case_word = word.lower()
    return [lower_case_word[i : i + 2] for i in range(len(lower_case_word) - 1)]


def unique_bigrams(bigrams: list[str]) -> set[str]:
    return set(bigrams)


def shared_bigrams(unique_bigrams1: set[str], unique_bigrams2: set[str]) -> set[str]:
    """Calculate the shared bigrams between two sets of bigrams.

    Args:
        unique_bigrams1: The first set of bigrams.
        unique_bigrams2: The second set of bigrams.

    Returns:
        A set containing the shared bigrams between the two lists.
    """
    return unique_bigrams1.intersection(unique_bigrams2)


def dice_match_word_pair(
    word1: str, word2: str, dice_min_counting_score: float
) -> bool:
    """Check if the Dice coefficient similarity score meets a given threshold.

    The Dice coefficient is calculated based on the number of shared bigrams
    (two-character sequences) between the two words, normalized by the total
    number of bigrams in both words.

    Args:
        word1: The first word to compare.
        word2: The second word to compare.
        dice_min_counting_score: The minimum Dice coefficient score
            required for the function to return True.

    Returns:
        True if the Dice coefficient score is greater than or equal to
        `dice_min_counting_score`, False otherwise.
    """

    unique_bigrams1 = unique_bigrams(string_to_bigram(word1.lower()))
    unique_bigrams2 = unique_bigrams(string_to_bigram(word2.lower()))

    if not unique_bigrams1 or not unique_bigrams2:
        return False

    dice_score = (2 * len(shared_bigrams(unique_bigrams1, unique_bigrams2))) / (
        len(unique_bigrams1) + len(unique_bigrams2)
    )

    return dice_score >= dice_min_counting_score


def dice_match_word_with_phrase(word: str, phrase: tuple[str, str]) -> bool:
    """Determines whether a word matches a phrase based on the Dice coefficient.

    This function calculates the Dice coefficient for bigrams shared between
    a given word and the words in a phrase. The match is considered valid if the Dice
    coefficient for both comparisons meets or exceeds the specified minimum score.

    Args:
        word: The word in the comparison.
        phrase: The phrase in the comparison.

    Returns:
        bool: True if both Dice coefficients meet or exceed the minimum score,
              False otherwise.
    """
    word_bigrams = unique_bigrams(string_to_bigram(word.lower()))

    phrase_bigrams = (
        unique_bigrams(string_to_bigram(phrase_word.lower())) for phrase_word in phrase
    )

    dice_scores = (
        (
            len(shared_bigrams(word_bigrams, phrase_bigram)) / len(phrase_bigram)
            if phrase_bigram
            else 0.0
        )
        for phrase_bigram in phrase_bigrams
    )

    return all(
        dice_score >= constants.DEFAULT_DICE_MIN_COUNTING_SCORE
        for dice_score in dice_scores
    )


def is_word_anchor_match(compiled_anchor_pattern: re.Pattern, word: str) -> bool:
    """Check if the word is an occurrence of the anchor word

    Args:
        compiled_anchor_pattern: A compiled regex pattern for matching anchor words.
        word: The word to check against the anchor pattern.

    Returns:
        True if the word matches the anchor pattern, False otherwise.
    """
    return bool(compiled_anchor_pattern.match(word))


def bad_length_correlation(lengths: list[int], ratio: float) -> bool:
    """Determine if the length correlation between two sequences is unacceptable.

    This function calculates a correlation value based on the lengths of two
    sequences and a given ratio. It checks if the correlation exceeds a
    predefined kill limit and if the element counts of the sequences differ.

    Args:
        lengths: The lengths of the entities.
        ratio: The ratio used to calculate the correlation.

    Returns:
        True if the correlation is above the kill limit and the element counts
        differ; otherwise, False.
    """
    kill_limit = 0.5
    # less tolerant limit for 1-2 and 2-1,
    # above which such alignments score lethally low
    length_correlation_factor = calculate_length_correlation_factor(lengths, ratio)
    return length_correlation_factor > kill_limit


def calculate_length_correlation_factor(lengths: list[int], ratio: float) -> float:
    """Calculate the length correlation factor between two lengths using a given ratio.

    Args:
        length1: The length of the first entity.
        length2: The length of the second entity.
        ratio: A ratio used to scale the lengths for correlation calculation.

    Returns:
        The length correlation factor as a float.
    """
    return (
        2
        * abs(0.0 + ratio * lengths[0] - lengths[1])
        / (ratio * lengths[0] + lengths[1])
    )


def adjust_for_length_correlation(
    score: float,
    lengths: list[int],
    element_counts: list[int],
    ratio: float,
) -> float:
    """
    Adjusts a similarity score based on length and element count correlation.

    This function modifies the input score by considering the correlation
    between the lengths and element counts of two entities, as well as a
    specified ratio. The adjustment is determined by a calculated correlation
    factor and predefined thresholds.

    Args:
        score: The initial similarity score to be adjusted.
        lengths: The lengths of the entities.
        element_counts: The number of elements in the entities.
        ratio: A ratio used to scale the lengths for correlation calculation.

    Returns:
        The adjusted similarity score based on the correlation analysis.
    """
    lower_limit = 0.4
    upper_limit = 1.0
    length_correlation_factor = calculate_length_correlation_factor(lengths, ratio)

    if length_correlation_factor < lower_limit / 2:
        return score + 2

    if length_correlation_factor < lower_limit:
        return score + 1

    if length_correlation_factor > upper_limit and not (
        all(element_counts) and element_counts[0] != element_counts[1]
    ):
        return score / 3

    # if length_correlation_factor is between lower_limit and upper_limit
    return score
