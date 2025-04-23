from dataclasses import dataclass

from python_tca2.aligned_sentence_elements import AlignedSentenceElements
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

    def valid_pairs(self) -> list[tuple[str, ...]]:
        """Return a list of valid tuple of elements from the alignments.

        A valid tuple is a tuple of elements from the alignments that have element
        numbers for all files.

        Returns:
            A list of tuples containing valid pairs of strings.
        """
        return [
            alignment_etc.to_tuple()
            for alignment_etc in self.alignments
            if all(aelements for aelements in alignment_etc.elements)
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
                                    for element in alignments_etc.elements[text_number]
                                ]
                            )
                            for alignments_etc in self.alignments
                        ]
                    ),
                    file=f,
                )
