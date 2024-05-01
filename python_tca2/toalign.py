import json
from collections import defaultdict

from python_tca2 import constants
from python_tca2.aelement import AElement
from python_tca2.alignments_etc import AlignmentsEtc
from python_tca2.link import Link


class ToAlign:
    def __init__(self):
        self.elements: defaultdict[int, list[AElement]] = defaultdict(list)
        self.pending: Link = None
        self.first_alignment_number = 0

    def to_json(self):
        return {
            "elements": [
                [lang_element.to_json() for lang_element in lang_elements]
                for lang_elements in self.elements.values()
            ],
            "pending": self.pending.to_json(),
        }

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def empty(self) -> bool:
        return len(self.pending) == 0

    def pickup(self, t: int, element: AElement):
        if element is not None:
            if self.pending is None:
                self.pending = Link()
                self.pending.alignment_number = self.first_alignment_number

            self.pending.element_numbers[t].append(element.element_number)
            last_alignment_number = self.first_alignment_number

            element.alignment_number = last_alignment_number
            self.elements[t].append(element)

    def flush(self) -> AlignmentsEtc:
        if self.pending:
            self.first_alignment_number = self.pending.alignment_number + 1
            return_value = AlignmentsEtc()
            return_value.alignments = self.pending
            for t in range(constants.NUM_FILES):
                while len(self.elements[t]) > 0:
                    return_value.elements[t].append(self.elements[t].pop(0))
            self.pending = None
            return return_value
        print("Nothing to flush")
