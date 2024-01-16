import json
from typing import List

from python_tca2 import constants
from python_tca2.aelement import AElement
from python_tca2.alignments_etc import AlignmentsEtc
from python_tca2.link import Link


class ToAlign:
    def __init__(self):
        self.elements: List[List[AElement]] = [[], []]
        self.pending: List[Link] = []
        self.first_alignment_number = 0

    def to_json(self):
        return {
            "elements": [
                [lang_element.to_json() for lang_element in lang_elements]
                for lang_elements in self.elements
            ],
            "pending": [al.to_json() for al in self.pending],
        }

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def empty(self) -> bool:
        return len(self.pending) == 0

    def pickup(self, t: int, element: AElement):
        if element is not None:
            if len(self.pending) == 0:
                new_link = Link()
                new_link.alignment_number = self.first_alignment_number
                self.pending.append(new_link)

            self.pending[-1].element_numbers[t].append(element.element_number)
            last_alignment_number = self.first_alignment_number + len(self.pending) - 1

            element.alignment_number = last_alignment_number
            self.elements[t].append(element)

    def flush(self) -> AlignmentsEtc:
        if self.pending:
            self.first_alignment_number = self.pending[-1].alignment_number + 1
            return_value = AlignmentsEtc()
            while len(self.pending) > 0:
                return_value.alignments.append(self.pending.pop(0))
            for t in range(constants.NUM_FILES):
                while len(self.elements[t]) > 0:
                    return_value.elements[t].append(self.elements[t].pop(0))
            return return_value
        print("Nothing to flush")
