from collections import defaultdict
from dataclasses import asdict, dataclass, field

from python_tca2.aelement import AElement


@dataclass
class TextPair:
    elements: defaultdict[int, list[AElement]] = field(
        default_factory=lambda: defaultdict(list)
    )
    start_position: list[int] = field(default_factory=lambda: [-1, -1])

    def get_next_element(self, text_number: int) -> AElement:
        self.start_position[text_number] += 1
        return self.elements[text_number][self.start_position[text_number]]

    def to_json(self):
        return {
            "elements": [
                asdict(element)
                for elements in self.elements.values()
                for element in elements
            ]
        }
