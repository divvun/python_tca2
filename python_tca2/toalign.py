from collections import defaultdict
from dataclasses import dataclass

from python_tca2.aelement import AElement
from python_tca2.alignments_etc import AlignmentsEtc


@dataclass
class ToAlign:
    elements: defaultdict[int, list[AElement]]

    def pickup(self, t: int, element: AElement):
        if element is not None:
            self.elements[t].append(element)

    def flush(self) -> AlignmentsEtc:
        if any(elements for elements in self.elements.values()):
            return_value = AlignmentsEtc(self.elements)
            self.elements = defaultdict(list)

            return return_value
        print("Nothing to flush")
