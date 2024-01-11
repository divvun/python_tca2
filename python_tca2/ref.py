import json


class Ref:
    def __init__(self, match_type, weight, t, element_number, pos, length, word):
        self.match_type = match_type
        self.weight = weight
        self.t = t
        self.element_number = element_number
        self.pos = pos
        self.length = length
        self.word = word

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def to_json(self):
        return {
            "match_type": self.match_type,
            "weight": self.weight,
            "t": self.t,
            "element_number": self.element_number,
            "pos": self.pos,
            "length": self.length,
            "word": self.word,
        }

    def matches(self, other_ref):
        if (
            (self.t == other_ref.t)
            and (self.element_number == other_ref.element_number)
            and (self.pos <= other_ref.pos + other_ref.length - 1)
            and (other_ref.pos <= self.pos + self.length - 1)
        ):
            return True
        elif other_ref.match_type >= 0:
            if self.match_type == other_ref.match_type:
                return True
        return False

    def is_in_text(self, t):
        return self.t == t

    def exactly_matches(self, other_ref):
        return (
            (self.match_type == other_ref.match_type)
            and (self.t == other_ref.t)
            and (self.element_number == other_ref.element_number)
            and (self.pos == other_ref.pos)
            and (self.length == other_ref.length)
        )

    def type_anchor_word(self):
        return self.match_type >= 0
