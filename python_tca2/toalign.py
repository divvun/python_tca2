import json
from collections import defaultdict
from dataclasses import asdict

from python_tca2.aelement import AElement
from python_tca2.alignments_etc import AlignmentsEtc


class ToAlign:
    def __init__(self):
        self.elements: defaultdict[int, list[AElement]] = defaultdict(list)
        self.first_alignment_number = 0

    def to_json(self):
        return {
            "elements": [
                [asdict(lang_element) for lang_element in lang_elements]
                for lang_elements in self.elements.values()
            ],
        }

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def empty(self) -> bool:
        return len(self.pending) == 0

    def pickup(self, t: int, element: AElement):
        if element is not None:
            element.alignment_number = self.first_alignment_number
            self.elements[t].append(element)

    def flush(self) -> AlignmentsEtc:
        if any(elements for elements in self.elements.values()):
            self.first_alignment_number += 1
            return_value = AlignmentsEtc(self.elements)
            self.elements = defaultdict(list)

            return return_value
        print("Nothing to flush")
