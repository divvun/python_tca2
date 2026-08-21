from dataclasses import dataclass
from functools import cached_property

from python_tca2 import constants
from python_tca2.anchorwordhits import AnchorWordHits


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



@dataclass
class AlignmentElement:
    text_number: int
    sentence: str
    element_number: int
    anchor_word_hits: AnchorWordHits

    @cached_property
    def text(self) -> str:
        return " ".join(self.sentence.split())

    @cached_property
    def length(self) -> int:
        return len(self.text)

    @cached_property
    def words(self) -> list[str]:
        return [
            rword
            for rword in [remove_special_characters(word) for word in self.text.split()]
            if rword.strip()
        ]

    @cached_property
    def num_words(self) -> int:
        return len(self.words)

    @cached_property
    def scoring_characters(self) -> str:
        return "".join(
            char for char in self.text if char in constants.DEFAULT_SCORING_CHARACTERS
        )
