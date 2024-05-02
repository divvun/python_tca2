from dataclasses import dataclass


@dataclass
class Ref:
    match_type: int
    weight: float
    t: int
    element_number: int
    pos: int
    length: int
    word: str

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

    def type_anchor_word(self):
        return self.match_type >= 0
