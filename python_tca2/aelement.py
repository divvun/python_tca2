import json


class AElement:
    def __init__(self, text, element_number):
        self.text = text
        self.element_number = element_number
        self.alignment_number = -1
        self.length = len(self.text)

    def to_json(self):
        return {
            "element": self.text,
            "element_number": self.element_number,
            "alignment_number": self.alignment_number,
            "length": self.length,
        }

    def __eq__(self, other):
        return (
            self.element_number == other.element_number
            and self.alignment_number == other.alignment_number
            and self.length == other.length
            and self.text == other.text
        )

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)
