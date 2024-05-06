from collections import defaultdict
from dataclasses import asdict, dataclass, field

from python_tca2.aelement import AElement


@dataclass
class TextPair:
    """Represents a pair of texts with associated elements.

    Attributes:
        elements (defaultdict[int, list[AElement]]): A dictionary that maps text
            numbers to lists of AElement objects.
        start_position (list[int]): A list that stores the current position of each
            text in the elements list. Starts off by one less than the first element,
            because the rest of the system expects it to that way.
            Q: Why does the rest of the system expect it to start off by one?
    """

    elements: defaultdict[int, list[AElement]] = field(
        default_factory=lambda: defaultdict(list)
    )
    start_position: list[int] = field(default_factory=lambda: [-1, -1])

    def get_next_element(self, text_number: int) -> AElement:
        """
        Returns the next AElement object for the specified text number.

        Args:
            text_number (int): The number of the text for which to retrieve the next
                element.

        Returns:
            AElement: The next AElement object for the specified text number.
        """
        self.start_position[text_number] += 1
        return self.elements[text_number][self.start_position[text_number]]

    def to_json(self):
        """
        Converts the TextPair object to a JSON-compatible dictionary.

        Returns:
            dict: A dictionary representation of the TextPair object.
        """
        return {
            "elements": [
                asdict(element)
                for elements in self.elements.values()
                for element in elements
            ]
        }
