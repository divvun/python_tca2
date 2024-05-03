from python_tca2.similarity_utils import dice_match1


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
