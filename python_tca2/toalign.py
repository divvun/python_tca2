from collections import defaultdict
from dataclasses import dataclass

from python_tca2.aelement import AElement
from python_tca2.alignments_etc import AlignmentsEtc


@dataclass
class ToAlign:
    elements: defaultdict[int, list[AElement]]
    first_alignment_number: int = 0

    def to_json(self):
        return {"elements": dict(self.elements)}

    def empty(self) -> bool:
        return all(len(elements) == 0 for elements in self.elements.values())

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
