from typing import List

from python_tca2 import constants
from python_tca2.alignment_suggestion import AlignmentSuggestion


class Tca2Path:
    """Represents a navigational path with alignment_suggestions and positional updates.

    Attributes:
        alignment_suggestions: A list of AlignmentSuggestions representing the path's
            alignment suggestions.
        position: A list representing the current position in the path.
    """

    def __init__(self, initial_position: list[int]) -> None:
        self.alignment_suggestions: List[AlignmentSuggestion] = []
        self.position = initial_position

    def to_json(self):
        return {
            "alignment_suggestions": [
                alignment_suggestion.to_json()
                for alignment_suggestion in self.alignment_suggestions
            ],
            "position": self.position,
        }

    def __eq__(self, path):
        return str(self) == str(path)

    def extend(self, aligment_suggestion: AlignmentSuggestion) -> None:
        """Extend the current path with a cloned step and update positions.

        Args:
            aligment_suggestion: The path step to be added and used for position
                updates.
        """
        self.alignment_suggestions.append(aligment_suggestion)
        for text_number in range(constants.NUM_FILES):
            self.position[text_number] += aligment_suggestion[text_number]

    def __str__(self):
        return (
            f"[{', '.join([str(step) for step in self.alignment_suggestions])}]->"
            + "{"
            + f"{self.position[0]},{self.position[1]}"
            + "}"
        )

    def get_length_in_sentences(self):
        """Calculate the total number of sentences across all alignment suggestions.

        Iterates through the alignment suggestions and sums up the sentence increments
        for each text to compute the total count.

        Returns:
            The total count of sentences.
        """
        return sum(
            increment_number
            for alignment_suggestion in self.alignment_suggestions
            for increment_number in alignment_suggestion
        )
