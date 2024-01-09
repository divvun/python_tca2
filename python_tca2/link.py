import json

from python_tca2 import constants


class Link:
    def __init__(self):
        self.alignment_number = -1
        self.element_numbers = [[] for _ in range(constants.NUM_FILES)]

    def __eq__(self, other):
        return self.alignment_number == other.alignment_number and all(
            e1e == e2e
            for e1, e2 in zip(self.element_numbers, other.element_numbers, strict=True)
            for e1e, e2e in zip(e1, e2, strict=True)
        )

    def to_json(self):
        return {
            "alignment_number": self.alignment_number,
            "element_numbers": self.element_numbers,
        }

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)
