from python_tca2.similarity_utils import (
    adjust_for_length_correlation,
    bad_length_correlation,
    dice_match_word_pair,
    dice_match_word_with_phrase,
)


def test_dice_match1():
    # Test case 1: Matching words with a dice score above the threshold
    assert dice_match_word_pair("hello", "hola", 0.5) is False

    # Test case 2: Matching words with a dice score below the threshold
    assert dice_match_word_pair("hello", "world", 0.8) is False

    # Test case 3: Matching words with an empty string
    assert dice_match_word_pair("", "", 0.5) is False

    # Test case 4: Matching words with one empty string
    assert dice_match_word_pair("hello", "", 0.5) is False

    # Test case 5: Matching words with special characters
    assert dice_match_word_pair("hello!", "hello?", 0.5) is True

    # Test case 6: Matching words with different letter cases
    assert dice_match_word_pair("Hello", "hello", 0.5) is True

    # Test case 7: Matching words with no shared bigrams
    assert dice_match_word_pair("apple", "banana", 0.5) is False


def test_adjust_for_length_correlation():
    # Test case 1: Matching words with same lengths and element counts
    assert adjust_for_length_correlation(0.0, [5, 5], [3, 3], 0.5) == 0.0

    # Test case 2: Matching words with different lengths and same element counts
    assert adjust_for_length_correlation(0.0, [5, 7], [3, 3], 0.5) == 0.0

    # Test case 3: Matching words with c < lower_limit / 2
    assert adjust_for_length_correlation(0.0, [5, 5], [3, 3], 0.1) == 0.0

    # Test case 4: Matching words with lower_limit / 2 < c < lower_limit
    assert adjust_for_length_correlation(0.0, [5, 5], [3, 3], 0.3) == 0.0

    # Test case 5: Matching words with c > upper_limit
    assert adjust_for_length_correlation(0.0, [5, 5], [3, 3], 0.9) == 2.0

    # Test case 6: Matching words with lower_limit < c < upper_limit
    assert adjust_for_length_correlation(0.0, [5, 5], [3, 3], 0.7) == 1.0


def test_bad_length_correlation():
    # Test case 1: Matching words with different lengths, c > kill_limit
    assert bad_length_correlation([5, 7], 0.5) is True

    # Test case 2: Matching words with same lengths, c > kill_limit
    assert bad_length_correlation([5, 5], 0.5) is True


def test_dice_match2():
    assert dice_match_word_with_phrase(phrase=("", ""), word="") is False
    assert (
        dice_match_word_with_phrase(phrase=("apple", "banana"), word="world") is False
    )
    assert (
        dice_match_word_with_phrase(phrase=("hello!", "hello?"), word="world") is False
    )
    assert dice_match_word_with_phrase(phrase=("hello", ""), word="world") is False
    assert dice_match_word_with_phrase(phrase=("Hello", "hello"), word="world") is False
    assert dice_match_word_with_phrase(phrase=("hello", "hola"), word="world") is False
    assert dice_match_word_with_phrase(phrase=("hello", "world"), word="") is False
