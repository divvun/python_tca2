import json
from collections import defaultdict

from python_tca2.aelement import AElement


class Unaligned:
    def __init__(self):
        self.elements: defaultdict[int, list[AElement]] = defaultdict(list)

    def pop(self, t: int) -> AElement:
        return self.elements[t].pop(0)

    def add_elements(self, elements: list[AElement], t: int):
        self.elements[t] = elements

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def to_json(self):
        return {
            "elements": [
                element.to_json()
                for elements in self.elements.values()
                for element in elements
            ]
        }
