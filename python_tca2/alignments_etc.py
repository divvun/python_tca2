from collections import defaultdict
from dataclasses import dataclass

from python_tca2.aelement import AElement


@dataclass
class AlignmentsEtc:
    elements: defaultdict[int, list[AElement]]

    def to_tuple(self) -> tuple[str, ...]:
        """Convert the elements of the object into a tuple of strings.

        Iterates over the values of the `elements` attribute, joining the text
        of each sub-element with a space, and returns the result as a tuple.
        """
        return tuple(
            " ".join([aelement.text for aelement in aelements])
            for aelements in self.elements.values()
        )
