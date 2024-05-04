from dataclasses import dataclass

from python_tca2.path import Path


@dataclass
class QueueEntry:
    path: Path
    score: float
    removed: bool = False
    end: bool = False

    def remove(self):
        self.removed = True

    def has_hit(self, pos: list[int]) -> bool:
        """Determines if a given position is a hit in the queue.

        Args:
            pos: The position to check.

        Returns:
            bool: True if the position is a hit, False otherwise.
        """
        current = list(self.path.position)

        if current == pos:
            return True

        for step in reversed(self.path.steps):
            # hvorfor trekkes step.increment fra current?
            # treffer den noe som helst med det?
            current[0] -= step.increment[0]
            current[1] -= step.increment[1]
            if current == pos:
                return True

        return False
