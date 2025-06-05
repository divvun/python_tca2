import re
from collections import defaultdict

from python_tca2 import constants


class AnchorWordListEntry:
    def __init__(self, anchor_word_list_entry_text: str):
        self.language: defaultdict[int, list[list[re.Pattern[str]]]] = defaultdict(list)

        if anchor_word_list_entry_text:
            pairs = anchor_word_list_entry_text.split("/")

            if len(pairs) < constants.NUM_FILES:
                raise Exception("No slash: " + anchor_word_list_entry_text)  # §§§
            elif len(pairs) > constants.NUM_FILES:
                raise Exception(
                    "Too many slashes: " + anchor_word_list_entry_text
                )  # §§§

            self.language.update(
                {
                    text_number: [
                        phrase
                        for phrase in self.make_phrases(data.split(","))
                        if phrase
                    ]
                    for text_number, data in enumerate(pairs)
                }
            )

    def make_phrases(self, pairs: list[str]) -> list[list[re.Pattern[str]]]:
        """Generate a list of phrase patterns from input pairs.

        Args:
            pairs: A list of strings, where each string contains comma-separated
                phrases.

        Returns:
            A list of lists, where each inner list contains compiled regex
            patterns for the phrases.
        """
        return [
            self.make_phrase(syn)
            for _, data in enumerate(pairs)
            for syn in data.split(",")
        ]

    def make_phrase(self, syn: str) -> list[re.Pattern[str]]:
        """Generates a list of compiled regex patterns from a synonym phrase.

        Args:
            syn: A string containing words separated by spaces.

        Returns:
            A list of compiled regex patterns for each non-empty word.
        """
        return [
            self.make_compiled_pattern(word)
            for word in syn.split(" ")
            if word.strip() != ""
        ]

    def make_compiled_pattern(self, anchor_word: str) -> re.Pattern[str]:
        """Make a proper regular expression from the anchor word"""
        pattern = "^" + anchor_word.replace("*", ".*") + "$"
        return re.compile(pattern, re.IGNORECASE | re.UNICODE)
