from typing import List

from python_tca2.path import Path


class QueueEntry:
    def __init__(self, position: List[int], score: float):
        self.path = Path(position)
        self.score = score
        self.removed: bool = False
        self.end: bool = False

    def remove(self):
        self.removed = True

    def __str__(self):
        score = f"{self.score:.2f}".replace(".", ",")
        return (
            f"QueueEntry: {self.path} {score} "
            f"{'true' if self.removed else 'false'} {'true' if self.end else 'false'}"
        )

    def to_json(self):
        return {
            "path": self.path.to_json(),
            "score": self.score,
            "removed": self.removed,
            "end": self.end,
        }
