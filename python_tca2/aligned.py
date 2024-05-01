import json

from python_tca2.alignments_etc import AlignmentsEtc


class Aligned:
    def __init__(self):
        self.alignments: list[AlignmentsEtc] = []

    def to_json(self):
        return {
            "alignments": [al.to_json() for al in self.alignments],
        }

    def __eq__(self, other):
        return self.elements == other.elements and self.alignments == other.alignments

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

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
