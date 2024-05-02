from typing import List

from python_tca2 import similarity_utils
from python_tca2.anchorwordhit import AnchorWordHit
from python_tca2.anchorwordhits import AnchorWordHits
from python_tca2.anchorwordlistentry import AnchorWordListEntry


class AnchorWordList:
    def __init__(self):
        self.entries: List[AnchorWordListEntry] = []

    def load_from_file(self, from_file):
        with open(from_file, "r") as file:
            self.entries = [AnchorWordListEntry(line.strip()) for line in file]

    def get_synonyms(self, t):
        return [
            (anchor_word_entry_count, anchor_phrase)
            for anchor_word_entry_count, entry in enumerate(self.entries)
            for anchor_phrase in entry.language[t]
        ]

    def get_anchor_word_hits(self, words, t, element_number):
        return AnchorWordHits(
            [
                AnchorWordHit(
                    anchor_word_entry_count,
                    element_number,
                    w,
                    " ".join(matching_phrase),
                )
                for anchor_word_entry_count, anchor_phrase in self.get_synonyms(t)
                for w in range(len(words) - len(anchor_phrase) + 1)
                for success, matching_phrase in [
                    self.found_success(words, anchor_phrase, w)
                ]
                if success
            ]
        )

    @staticmethod
    def found_success(words, anchor_phrase, w):
        success = True
        matching_phrase = []  # the actual phrase occurring in the text
        for w2 in range(len(anchor_phrase)):
            word = words[w + w2]
            if not similarity_utils.anchor_match(
                compiled_anchor_pattern=anchor_phrase[w2], word=word
            ):
                return False, []

            if w2 > 0:
                matching_phrase.append(" ")
            matching_phrase.append(word)

        return success, matching_phrase
