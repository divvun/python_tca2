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
        current_ix = len(self.path.steps) - 1

        while current_ix > -1:
            if all(
                current[text_number] == pos[text_number]
                for text_number in range(len(pos))
            ):
                return True

            for text_number in range(len(pos)):
                current[text_number] -= self.path.steps[current_ix].increment[
                    text_number
                ]
            current_ix -= 1

        return False
