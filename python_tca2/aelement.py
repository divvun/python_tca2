from dataclasses import dataclass


@dataclass
class AlignmentElement:
    """A class representing a sentence in a document.

    Attributes:
        text: A sentence.
        element_number: The position of the sentence in the document.

    Properties:
        length (int): The length of the sentence.
    """

    text: str
    element_number: int

    @property
    def length(self) -> int:
        return len(self.text)
