from dataclasses import dataclass, field

from python_tca2.alignment_suggestion import AlignmentSuggestion


@dataclass
class QueueEntry:
    """Represents an entry in a processing queue.

    Attributes:
        path: The path associated with the queue entry.
        score: The score or priority of the queue entry.
        removed: Indicates if the entry has been removed.
        end: Indicates if the entry marks the end of the queue.

    Properties:
        normalized_score (float): The normalized score of the queue entry, calculated as
            the score divided by the length of the path in sentences.
    """

    position: list[int]
    score: float = 0.0
    alignment_suggestions: list[AlignmentSuggestion] = field(default_factory=list)
    end: bool = False

    @property
    def normalized_score(self) -> float:
        """Calculates the normalized score of the queue entry.

        Returns:
            float: The normalized score.
        """
        return self.score / self.get_length_in_sentences()

    def has_hit(self, pos: list[int]) -> bool:
        """Determines if a given position is a hit in the queue.

        Args:
            pos: The position to check.

        Returns:
            bool: True if the position is a hit, False otherwise.
        """
        current = list(self.position)

        if current == pos:
            return True

        for step in reversed(self.alignment_suggestions):
            # hvorfor trekkes step.increment fra current?
            # treffer den noe som helst med det?
            current[0] -= step[0]
            current[1] -= step[1]
            if current == pos:
                return True

        return False

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
