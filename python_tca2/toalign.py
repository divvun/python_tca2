from collections import defaultdict
from dataclasses import dataclass

from python_tca2.aelement import AlignmentElement
from python_tca2.aligned_sentence_elements import AlignedSentenceElements


@dataclass
class ToAlign:
    """A class to manage and align elements for text processing.

    Attributes:
        elements: A defaultdict mapping text numbers to lists of elements.
    """

    elements: defaultdict[int, list[AlignmentElement]]

    def pickup(self, text_number: int, element: AlignmentElement) -> None:
        """Adds an element to the specified text number's elements list.

        Args:
            text_number: The index of the text to which the element belongs.
            element: The element to be added to the list.
        """
        if element is not None:
            self.elements[text_number].append(element)

    def flush(self) -> AlignedSentenceElements | None:
        """Flushes and returns accumulated elements if any exist.

        If there are elements in the internal storage, creates an AlignmentsEtc
        object with the current elements, resets the storage, and returns the
        created object. If no elements exist, prints a message and returns None.

        Returns:
            An AlignmentsEtc object if elements exist, otherwise None.
        """
        if any(elements for elements in self.elements.values()):
            return_value = AlignedSentenceElements(self.elements)
            self.elements = defaultdict(list)

            return return_value

        print("Nothing to flush")
        return None
