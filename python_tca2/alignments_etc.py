from collections import defaultdict
from dataclasses import dataclass

from python_tca2.aelement import AElement


@dataclass
class AlignmentsEtc:
    elements: defaultdict[int, list[AElement]]

    def to_tuple(self):
        return tuple(
            " ".join([aelement.text for aelement in aelements])
            for aelements in self.elements.values()
        )
