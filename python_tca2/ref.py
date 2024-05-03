from dataclasses import dataclass


@dataclass
class Ref:
    match_type: int
    weight: float
    text_number: int
    element_number: int
    pos: int
    length: int
    word: str

    def matches(self, other_ref):
        if (
            (self.text_number == other_ref.text_number)
            and (self.element_number == other_ref.element_number)
            and (self.pos <= other_ref.pos + other_ref.length - 1)
            and (other_ref.pos <= self.pos + self.length - 1)
        ):
            return True
        elif other_ref.match_type >= 0:
            if self.match_type == other_ref.match_type:
                return True
        return False

    def is_in_text(self, text_number):
        return self.text_number == text_number

    def type_anchor_word(self):
        return self.match_type >= 0
