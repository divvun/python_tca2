from dataclasses import dataclass

from python_tca2.alignments_etc import AlignmentsEtc


@dataclass
class Aligned:
    alignments: list[AlignmentsEtc]

    def pickup(self, value_got: AlignmentsEtc):
        if value_got is not None:
            self.alignments.append(value_got)

    def valid_pairs(self) -> list[tuple[str, str]]:
        """Return a list of valid tuple of elements from the alignments.

        A valid tuple is a tuple of elements from the alignments that have element
        numbers for all files.
        """
        return [
            alignment_etc.to_tuple()
            for alignment_etc in self.alignments
            if all(aelements for aelements in alignment_etc.elements.values())
        ]
