from dataclasses import dataclass

from python_tca2.aligned_sentence_elements import (
    AlignedSentenceElements,
    to_string_tuple,
)
from python_tca2.constants import NUM_FILES


@dataclass
class Aligned:
    alignments: list[AlignedSentenceElements]

    def pickup(self, aligned_sentence_elements: AlignedSentenceElements | None) -> None:
        """Adds aligned sentence elements to the alignments list.

        Args:
            aligned_sentence_elements: The alignment or related value to be added. If
                                        None, no action is taken.
        """
        if aligned_sentence_elements is not None:
            self.alignments.append(aligned_sentence_elements)

    def non_empty_pairs(self) -> list[tuple[str, str]]:
        """Create translation pairs containing non-empty strings.

        Returns:
            A list of tuples containing valid pairs of strings.
        """
        return [
            to_string_tuple(aligned_sentence_elements)
            for aligned_sentence_elements in self.alignments
            if all(aelements for aelements in aligned_sentence_elements)
        ]

    def save_plain(self) -> None:
        """Save aligned text data to plain text files.

        Iterates through a predefined number of text files, processes the
        alignments, and writes the aligned text data to separate plain text
        files named "aligned_<text_number>.txt".
        """
        for text_number in range(NUM_FILES):
            with open(f"aligned_{text_number}.txt", "w") as f:
                print(
                    "\n".join(
                        [
                            " ".join(
                                [
                                    element.text
                                    for element in alignments_etc[text_number]
                                ]
                            )
                            for alignments_etc in self.alignments
                        ]
                    ),
                    file=f,
                )
