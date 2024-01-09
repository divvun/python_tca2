from typing import List

from python_tca2 import constants
from python_tca2.aelement import AElement
from python_tca2.alignments_etc import AlignmentsEtc
from python_tca2.link import Link


class Aligned:
    def __init__(self):
        self.elements: List[List[AElement]] = [[] for _ in range(constants.NUM_FILES)]
        self.alignments: List[Link] = []

    def to_json(self):
        return {
            "elements": self.elements,
            "alignments": [al.to_json() for al in self.alignments],
        }

    def __eq__(self, other):
        return self.elements == other.elements and self.alignments == other.alignments

    def __str__(self):
        str_ = "Aligned: "
        str_ += "alignments: " + ", ".join(str(al) for al in self.alignments)
        str_ += " elements: " + "\n".join(
            str(el) for els in self.elements for el in els
        )
        return str_

    def pickup(self, value_got: AlignmentsEtc):
        if value_got is not None:
            self.alignments.extend(value_got.alignments)
            for t in range(constants.NUM_FILES):
                for i in range(len(value_got.elements[t])):
                    self.elements[t].append(value_got.elements[t][i])
