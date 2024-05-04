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
        return pos in self.path.position
