from python_tca2.similarity_utils import (
    adjust_for_length_correlation,
    bad_length_correlation,
    dice_match1,
    dice_match2,
)


def test_dice_match1():
    # Test case 1: Matching words with a dice score above the threshold
    assert dice_match1("hello", "hola", 0.5) is False

    # Test case 2: Matching words with a dice score below the threshold
    assert dice_match1("hello", "world", 0.8) is False

    # Test case 3: Matching words with an empty string
    assert dice_match1("", "", 0.5) is False

    # Test case 4: Matching words with one empty string
    assert dice_match1("hello", "", 0.5) is False

    # Test case 5: Matching words with special characters
    assert dice_match1("hello!", "hello?", 0.5) is True

    # Test case 6: Matching words with different letter cases
    assert dice_match1("Hello", "hello", 0.5) is True

    # Test case 7: Matching words with no shared bigrams
    assert dice_match1("apple", "banana", 0.5) is False


def test_adjust_for_length_correlation():
    # Test case 1: Matching words with same lengths and element counts
    assert adjust_for_length_correlation(0.0, 5, 5, 3, 3, 0.5) == 0.0

    # Test case 2: Matching words with different lengths and same element counts
    assert adjust_for_length_correlation(0.0, 5, 7, 3, 3, 0.5) == 0.0

    # Test case 3: Matching words with c < lower_limit / 2
    assert adjust_for_length_correlation(0.0, 5, 5, 3, 3, 0.1) == 0.0

    # Test case 4: Matching words with lower_limit / 2 < c < lower_limit
    assert adjust_for_length_correlation(0.0, 5, 5, 3, 3, 0.3) == 0.0

    # Test case 5: Matching words with c > upper_limit
    assert adjust_for_length_correlation(0.0, 5, 5, 3, 3, 0.9) == 2.0

    # Test case 6: Matching words with lower_limit < c < upper_limit
    assert adjust_for_length_correlation(0.0, 5, 5, 3, 3, 0.7) == 1.0


def test_bad_length_correlation():
    # Test case 1: Matching words with different lengths and element counts, c > kill_limit
    assert bad_length_correlation(5, 7, 3, 4, 0.5) is True

    # Test case 2: Matching words with same lengths and element counts, c <= kill_limit
    assert bad_length_correlation(5, 5, 3, 3, 0.5) is False

    # Test case 3: Matching words with different lengths and same element counts, c <= kill_limit
    assert bad_length_correlation(5, 7, 3, 3, 0.5) is False

    # Test case 4: Matching words with same lengths and different element counts, c > kill_limit
    assert bad_length_correlation(5, 5, 3, 4, 0.5) is True

    # Test case 5: Matching words with c < lower_limit / 2, c <= kill_limit
    assert bad_length_correlation(5, 5, 3, 3, 0.1) is False

    # Test case 6: Matching words with lower_limit / 2 < c < lower_limit, c <= kill_limit
    assert bad_length_correlation(5, 5, 3, 3, 0.3) is False

    # Test case 7: Matching words with c > upper_limit, c > kill_limit
    assert bad_length_correlation(5, 5, 3, 3, 0.9) is False

    # Test case 8: Matching words with lower_limit < c < upper_limit, c <= kill_limit
    assert bad_length_correlation(5, 5, 3, 3, 0.7) is False


def test_dice_match2():
    # Matching words with type "2-1" and dice scores above the threshold
    assert dice_match2("hello", "hola", "world", "2-1", 0.5) is False

    # Matching words with type "2-1" and dice scores below the threshold
    assert dice_match2("hello", "hola", "world", "2-1", 0.8) is False

    # Matching words with type "2-1" and empty strings
    assert dice_match2("", "", "", "2-1", 0.5) is False

    # Matching words with type "2-1" and one empty string
    assert dice_match2("hello", "", "world", "2-1", 0.5) is False

    # Matching words with type "2-1" and special characters
    assert dice_match2("hello!", "hello?", "world", "2-1", 0.5) is False

    # Matching words with type "2-1" and different letter cases
    assert dice_match2("Hello", "hello", "world", "2-1", 0.5) is False

    # Matching words with type "2-1" and no shared bigrams
    assert dice_match2("apple", "banana", "world", "2-1", 0.5) is False

    # Matching words with type "1-2" and dice scores above the threshold
    assert dice_match2("world", "hello", "hola", "1-2", 0.5) is False

    # Matching words with type "1-2" and dice scores below the threshold
    assert dice_match2("world", "hello", "hola", "1-2", 0.8) is False

    # Matching words with type "1-2" and empty strings
    assert dice_match2("", "", "", "1-2", 0.5) is False

    # Matching words with type "1-2" and one empty string
    assert dice_match2("", "hello", "world", "1-2", 0.5) is False

    # Matching words with type "1-2" and special characters
    assert dice_match2("world", "hello!", "hello?", "1-2", 0.5) is False

    # Matching words with type "1-2" and different letter cases
    assert dice_match2("world", "Hello", "hello", "1-2", 0.5) is False

    # Matching words with type "1-2" and no shared bigrams
    assert dice_match2("world", "apple", "banana", "1-2", 0.5) is False
