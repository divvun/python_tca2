from re import Pattern

from python_tca2 import similarity_utils
from python_tca2.anchorwordhit import AnchorWordHit
from python_tca2.anchorwordhits import AnchorWordHits
from python_tca2.anchorwordlistentry import AnchorWordListEntry


class AnchorWordList:
    """Represents a list of anchor words and provides methods to process them."""

    def __init__(self) -> None:
        self.entries: list[AnchorWordListEntry] = []

    def load_from_file(self, from_file: str) -> None:
        """Loads anchor word list entries from a specified file.

        Reads the file line by line, stripping whitespace, and creates a list of
        AnchorWordListEntry objects from the lines in the file.
        """
        with open(from_file, "r") as file:
            self.entries = [AnchorWordListEntry(line.strip()) for line in file]

    def get_synonyms(self, text_number: int) -> list[tuple[int, list[Pattern[str]]]]:
        """Retrieve synonyms for a given text number from the entries.

        Args:
            text_number: The index of the text to retrieve synonyms for.

        Returns:
            A list of tuples, where each tuple contains an anchor word entry
            count and a list of patterns representing synonyms.
        """
        return [
            (anchor_word_entry_count, anchor_phrase)
            for anchor_word_entry_count, entry in enumerate(self.entries)
            for anchor_phrase in entry.language[text_number]
        ]

    def get_anchor_word_hits(
        self, words: list[str], text_number: int, element_number: int
    ) -> AnchorWordHits:
        """Retrieves anchor word hits based on provided words and indices.

        Args:
            words: A list of words to search for anchor word hits.
            text_number: The identifier for the text to search within.
            element_number: The specific element number for the search.

        Returns:
            An AnchorWordHits object containing the matching anchor word hits.
        """
        return AnchorWordHits(
            [
                AnchorWordHit(
                    anchor_word_entry_count,
                    element_number,
                    w,
                    " ".join(matching_phrase),
                )
                for anchor_word_entry_count, anchor_phrase in self.get_synonyms(
                    text_number
                )
                for w in range(len(words) - len(anchor_phrase) + 1)
                for success, matching_phrase in [
                    self.found_success(words, anchor_phrase, w)
                ]
                if success
            ]
        )

    @staticmethod
    def found_success(
        words: list[str], anchor_phrase: list[Pattern[str]], w: int
    ) -> tuple[bool, list[str]]:
        """Checks if a sequence of words matches an anchor phrase pattern.

        Args:
            words: The list of words to check against the anchor phrase.
            anchor_phrase: The list of compiled regex patterns for the anchor phrase.
            w: The starting index in the words list to check from.

        Returns:
            A tuple containing a boolean indicating success and the matching phrase.
        """
        success = True
        matching_phrase: list[str] = []  # the actual phrase occurring in the text
        for w2 in range(len(anchor_phrase)):
            word = words[w + w2]
            if not similarity_utils.is_word_anchor_match(
                compiled_anchor_pattern=anchor_phrase[w2], word=word
            ):
                return False, []

            if w2 > 0:
                matching_phrase.append(" ")
            matching_phrase.append(word)

        return success, matching_phrase
