import json
from dataclasses import asdict

from python_tca2 import constants
from python_tca2.anchorwordhits import AnchorWordHits
from python_tca2.anchorwordlist import AnchorWordList


def remove_special_characters(word: str) -> str:
    """Removes special characters from the start and end of a word.

    Iterates through a predefined list of special characters and removes any
    occurrences of these characters from the beginning and end of the given word.
    Strips any remaining whitespace before returning the result.

    Parameters:
        word: The input string to process.

    Returns:
        The processed string with special characters removed.
    """
    for special_char in constants.DEFAULT_SPECIAL_CHARACTERS:
        if word.startswith(special_char):
            word = word[1:]
        if word.endswith(special_char):
            word = word[:-1]

    return word.strip()


def get_scoring_characters(text: str) -> str:
    """Extracts and returns scoring characters from the input text.

    Args:
        text: The input string to process.

    Returns:
        A string containing only the scoring characters found in the input text.
    """
    scoring_characters = constants.DEFAULT_SCORING_CHARACTERS
    ret = ""
    for i in range(len(text)):
        if text[i] in scoring_characters:
            ret += text[i]
    return ret


def get_upper_case_words(words: list[str]) -> list[str]:
    """Filters a list of words to include only those starting with an uppercase letter.

    Args:
        words: A list of words to filter.

    Returns:
        A list of words that start with an uppercase letter.
    """
    return [word for word in words if len(word) > 0 and word[0].isupper()]


# TODO: Looks like this can be merged with AEelement
# Most all attributes are essentially derived from AEelement info, anyway
class ElementInfo:
    def __init__(
        self,
        anchor_word_list: AnchorWordList,
        text: str,
        text_number: int,
        element_number: int,
    ) -> None:
        self.element_number = element_number
        self.length = len(text)
        self.words = [
            rword
            for rword in [remove_special_characters(word) for word in text.split()]
            if rword.strip()
        ]
        self.num_words = len(self.words)
        self.anchor_word_hits: AnchorWordHits = anchor_word_list.get_anchor_word_hits(
            self.words, text_number, element_number
        )
        self.upper_case_words = get_upper_case_words(self.words)
        self.scoring_characters = get_scoring_characters(text)

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def to_json(self):
        return {
            "element_number": self.element_number,
            "length": self.length,
            "num_words": self.num_words,
            "words": self.words,
            "anchor_word_hits": asdict(self.anchor_word_hits),
            "scoring_characters": self.scoring_characters,
            "proper_names": self.upper_case_words,
        }
