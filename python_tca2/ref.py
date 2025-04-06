from dataclasses import dataclass


@dataclass
class Ref:
    """Represents a reference with attributes and matching logic.

    Attributes:
        match_type: The type of match for the reference.
        weight: The weight or importance of the reference.
        text_number: The identifier of the text containing the reference.
        element_number: The identifier of the element within the text.
        pos: The starting position of the reference.
        length: The length of the reference.
        word: The word associated with the reference.
    """

    match_type: int
    weight: float
    text_number: int
    element_number: int
    pos: int
    length: int
    word: str

    def matches(self, other_ref: "Ref") -> bool:
        """Determines if this reference matches another reference.

        Args:
            other_ref: The reference to compare against.

        Returns:
            True if the references match based on text number, element number,
            position, length, or match type; otherwise, False.
        """
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
        """Check if the instance's text number matches the given number.

        Args:
            text_number: The text number to compare against.

        Returns:
            True if the instance's text number matches, False otherwise.
        """
        return self.text_number == text_number

    def type_anchor_word(self) -> bool:
        return self.match_type >= 0
