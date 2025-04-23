from dataclasses import dataclass, field

from python_tca2 import constants
from python_tca2.aelement import AlignmentElement


@dataclass
class ParallelDocuments:
    """Represents parallel texts.

    Attributes:
        elements: A tuple where each item is a list of AlignmentElement objects.
            Each list corresponds to a text, and each AlignmentElement
            represents a sentence in that text.

        start_position: A list that stores the current start position of each
            text in the elements list. Starts off by one less than the first element,
            because the rest of the system expects it to that way.
            Q: Why does the rest of the system expect it to start off by one?
    """

    elements: tuple[list[AlignmentElement], ...]
    start_position: list[int] = field(
        default_factory=lambda: [-1] * constants.NUM_FILES
    )

    def get_next_element(self, text_number: int) -> AlignmentElement:
        """Returns the next AlignmentElement object for the specified text number.

        Args:
            text_number (int): The number of the text for which to retrieve the next
                element.

        Returns:
            The next AlignmentElement object for the specified text number.
        """
        self.start_position[text_number] += 1
        return self.elements[text_number][self.start_position[text_number]]

    def to_json(self):
        """Converts the TextPair object to a JSON-compatible dictionary.

        Returns:
            dict: A dictionary representation of the TextPair object.
        """
        return {
            "elements": [
                element.to_json() for elements in self.elements for element in elements
            ]
        }
