import re


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


def dice_match1(word1: str, word2: str, dice_min_counting_score: float) -> bool:
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

    count_bigrams1 = len(unique_bigrams1)
    count_bigrams2 = len(unique_bigrams2)

    if not count_bigrams1 or not count_bigrams2:
        return False

    count_shared_bigrams = len(shared_bigrams(unique_bigrams1, unique_bigrams2))

    dice_score = (2 * count_shared_bigrams) / (count_bigrams1 + count_bigrams2)

    return dice_score >= dice_min_counting_score


def dice_match2(
    word_a: str, word_b: str, word_c: str, type_: str, dice_min_counting_score: float
) -> bool:
    """Determines whether a word matches a phrase based on the Dice coefficient.

    This function calculates the Dice coefficient for bigrams shared between
    a given word and two other words (forming a phrase). The match is considered
    valid if the Dice coefficient for both comparisons meets or exceeds the
    specified minimum score.

    Args:
        word_a: The first word in the comparison.
        word_b: The second word in the comparison.
        word_c: The third word in the comparison.
        type_: Specifies the type of comparison.
               - "2-1": `word_a` and `word_b` form the phrase, compared to `word_c`.
               - "1-2": `word_b` and `word_c` form the phrase, compared to `word_a`.
        dice_min_counting_score: The minimum Dice coefficient score required
                                 for a match to be considered valid.

    Returns:
        bool: True if both Dice coefficients meet or exceed the minimum score,
              False otherwise.
    """
    phrase_word1, phrase_word2 = "", ""
    word = ""

    if type_ == "2-1":
        phrase_word1 = word_a
        phrase_word2 = word_b
        word = word_c
    elif type_ == "1-2":
        word = word_a
        phrase_word1 = word_b
        phrase_word2 = word_c
    else:
        # ### program error
        return False

    unique_word_bigrams = unique_bigrams(string_to_bigram(word.lower()))
    unique_phrase1_bigrams = unique_bigrams(string_to_bigram(phrase_word1.lower()))
    unique_phrase2_bigrams = unique_bigrams(string_to_bigram(phrase_word2.lower()))

    count_bigrams_in_phrase_word1 = len(unique_phrase1_bigrams)
    count_bigrams_in_phrase_word2 = len(unique_phrase2_bigrams)

    count_shared_bigrams1 = len(
        shared_bigrams(unique_word_bigrams, unique_phrase1_bigrams)
    )
    count_shared_bigrams2 = len(
        shared_bigrams(unique_word_bigrams, unique_phrase2_bigrams)
    )

    dice_score1 = (
        count_shared_bigrams1 / count_bigrams_in_phrase_word1
        if count_bigrams_in_phrase_word1
        else 0.0
    )

    dice_score2 = (
        count_shared_bigrams2 / count_bigrams_in_phrase_word2
        if count_bigrams_in_phrase_word2
        else 0.0
    )

    return (dice_score1 >= dice_min_counting_score) and (
        dice_score2 >= dice_min_counting_score
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


def bad_length_correlation(
    length1: int, length2: int, element_count1: int, element_count2: int, ratio: float
) -> bool:
    """Determine if the length correlation between two sequences is unacceptable.

    This function calculates a correlation value based on the lengths of two
    sequences and a given ratio. It checks if the correlation exceeds a
    predefined kill limit and if the element counts of the sequences differ.

    Args:
        length1: The length of the first sequence.
        length2: The length of the second sequence.
        element_count1: The number of elements in the first sequence.
        element_count2: The number of elements in the second sequence.
        ratio: The ratio used to calculate the correlation.

    Returns:
        True if the correlation is above the kill limit and the element counts
        differ; otherwise, False.
    """
    kill_limit = 0.5
    # less tolerant limit for 1-2 and 2-1,
    # above which such alignments score lethally low
    length_correlation_factor = calculate_length_correlation_factor(
        length1, length2, ratio
    )
    return (
        element_count1 > 0 and element_count2 > 0 and element_count1 != element_count2
    ) and (length_correlation_factor > kill_limit)


def calculate_length_correlation_factor(
    length1: int, length2: int, ratio: float
) -> float:
    """Calculate the length correlation factor between two lengths using a given ratio.

    Args:
        length1: The length of the first entity.
        length2: The length of the second entity.
        ratio: A ratio used to scale the lengths for correlation calculation.

    Returns:
        The length correlation factor as a float.
    """
    return 2 * abs(0.0 + ratio * length1 - length2) / (ratio * length1 + length2)


def adjust_for_length_correlation(  # noqa: PLR0913
    score: float,
    length1: int,
    length2: int,
    element_count1: int,
    element_count2: int,
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
        length1: The length of the first entity.
        length2: The length of the second entity.
        element_count1: The number of elements in the first entity.
        element_count2: The number of elements in the second entity.
        ratio: A ratio used to scale the lengths for correlation calculation.

    Returns:
        The adjusted similarity score based on the correlation analysis.
    """
    lower_limit = 0.4
    upper_limit = 1.0
    length_correlation_factor = calculate_length_correlation_factor(
        length1, length2, ratio
    )

    if length_correlation_factor < lower_limit / 2:
        return score + 2

    if length_correlation_factor < lower_limit:
        return score + 1

    if length_correlation_factor > upper_limit and not (
        element_count1 > 0 and element_count2 > 0 and element_count1 != element_count2
    ):
        return score / 3

    # if length_correlation_factor is between lower_limit and upper_limit
    return score
