import json
from typing import List

from python_tca2.aelement import AElement


class Unaligned:
    def __init__(self):
        self.elements: List[List[AElement]] = [[], []]

    def pop(self, t: int) -> AElement:
        return self.elements[t].pop(0)

    def add(self, element: AElement, t: int):
        self.elements[t].append(element)

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def to_json(self):
        return {
            "elements": [
                element.to_json() for elements in self.elements for element in elements
            ]
        }
