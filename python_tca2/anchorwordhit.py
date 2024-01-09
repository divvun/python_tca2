import json


class AnchorWordHit:
    def __init__(self, index, element_number, pos, word):
        self.index = index
        self.element_number = element_number
        self.pos = pos
        self.word = word

    def get_index(self):
        return self.index

    def get_word(self):
        return self.word

    def get_pos(self):
        return self.pos

    def get_element_number(self):
        return self.elementNumber

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def to_json(self):
        return {
            "index": self.index,
            "element_number": self.element_number,
            "pos": self.pos,
            "word": self.word,
        }
