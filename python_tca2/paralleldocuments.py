from dataclasses import dataclass

from python_tca2.aelement import AlignmentElement
from python_tca2.aligned_sentence_elements import AlignedSentenceElements
from python_tca2.alignment_suggestion import AlignmentSuggestion


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
    start_position: tuple[int, ...]

    def get_aligned_sentence_elements(
        self, alignment_suggestion: AlignmentSuggestion
    ) -> AlignedSentenceElements:
        """Returns the next AlignmentElement object for the specified text number.


        Args:
            alignment_suggestion: How man elements to move in each text.

        Returns:
            A tuple of AlignmentElement objects for each text.
        """
        # TODO: fix the -1 issue
        return_tuple = tuple(
            alignment_elements[
                current_position
                + 1 : current_position
                + 1
                + number_of_elements  # + 1 here because first element starts at -1 …
            ]
            for (current_position, number_of_elements, alignment_elements) in zip(
                self.start_position, alignment_suggestion, self.elements, strict=True
            )
        )
        self.start_position = tuple(
            current_position + number_of_elements
            for (current_position, number_of_elements) in zip(
                self.start_position, alignment_suggestion, strict=True
            )
        )

        return AlignedSentenceElements(return_tuple)

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
