from collections import defaultdict
from dataclasses import asdict, dataclass

from python_tca2.aelement import AElement


@dataclass
class TextPair:
    elements: defaultdict[int, list[AElement]]

    def pop(self, text_number: int) -> AElement:
        return self.elements[text_number].pop(0)

    def to_json(self):
        return {
            "elements": [
                asdict(element)
                for elements in self.elements.values()
                for element in elements
            ]
        }
