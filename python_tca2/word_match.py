from dataclasses import dataclass


@dataclass
class WordMatch:
    """A single matched word occurrence, used to build scoring clusters."""

    match_type: int
    weight: float
    text_number: int
    element_number: int
    pos: int
    length: int
    word: str

    def overlaps(self, other_ref: "WordMatch") -> bool:
        """Check whether this match overlaps another in position or match type."""
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

    def is_in_text(self, text_number: int) -> bool:
        """Check if this match belongs to the given text."""
        return self.text_number == text_number
