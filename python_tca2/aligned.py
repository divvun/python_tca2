import json
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
            "elements": [
                [element.to_json() for element in elements]
                for elements in self.elements
            ],
            "alignments": [al.to_json() for al in self.alignments],
        }

    def __eq__(self, other):
        return self.elements == other.elements and self.alignments == other.alignments

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def pickup(self, value_got: AlignmentsEtc):
        if value_got is not None:
            self.alignments.extend(value_got.alignments)
            for t in range(constants.NUM_FILES):
                for i in range(len(value_got.elements[t])):
                    self.elements[t].append(value_got.elements[t][i])

    def valid_pairs(self) -> list[tuple[str, str]]:
        """Return a list of valid tuple of elements from the alignments.

        A valid tuple is a tuple of elements from the alignments that have element
        numbers for all files.
        """
        return [
            tuple(
                [
                    " ".join(
                        [
                            self.elements[index][element_number]["element"]
                            for element_number in element_numbers
                        ]
                    )
                    for index, element_numbers in enumerate(link["element_numbers"])
                ]
            )
            for link in self.alignments
            if all(element_numbers for element_numbers in link["element_numbers"])
        ]
