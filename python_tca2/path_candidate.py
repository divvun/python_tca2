from dataclasses import dataclass, field

from python_tca2.alignment_suggestion import AlignmentSuggestion


@dataclass
class PathCandidate:
    """A candidate alignment path being extended during beam search."""

    position: tuple[int, int]
    score: float = 0.0
    alignment_suggestions: list[AlignmentSuggestion] = field(
        default_factory=list[AlignmentSuggestion]
    )
    end: bool = False
    removed: bool = False

    @property
    def normalized_score(self) -> float:
        """Score divided by the path length in sentences, for comparing paths."""
        return self.score / self.get_length_in_sentences()

    def has_hit(self, pos: tuple[int, ...]) -> bool:
        """Check whether this path passed through pos at any point along its history."""
        current = list(self.position)

        if tuple(current) == pos:
            return True

        for step in reversed(self.alignment_suggestions):
            current[0] -= step[0]
            current[1] -= step[1]

            if current[0] < pos[0] or current[1] < pos[1]:
                return False

            if tuple(current) == pos:
                return True

        return False

    def get_length_in_sentences(self):
        """Total sentence increments across all alignment suggestions on this path."""
        return sum(
            increment_number
            for alignment_suggestion in self.alignment_suggestions
            for increment_number in alignment_suggestion
        )
