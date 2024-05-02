import json
from collections import defaultdict
from dataclasses import asdict, dataclass

from python_tca2.aelement import AElement


@dataclass
class Unaligned:
    elements: defaultdict[int, list[AElement]]

    def pop(self, t: int) -> AElement:
        return self.elements[t].pop(0)

    def add_elements(self, elements: list[AElement], t: int):
        self.elements[t] = elements

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def to_json(self):
        return {
            "elements": [
                asdict(element)
                for elements in self.elements.values()
                for element in elements
            ]
        }
