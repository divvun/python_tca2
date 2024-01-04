from typing import List

from python_tca2.path import Path


class QueueEntry:
    def __init__(self, position: List[int], score: float):
        # print_frame(f"position {position} score {score}")
        self.path = Path(position)
        self.score = score
        self.removed: bool = False
        self.end: bool = False

    def remove(self):
        # print_frame()
        self.removed = True

    def __str__(self):
        return (
            f"QueueEntry: {self.path} {self.score if self.score else "0.0"} "
            f"{'true' if self.removed else 'false'} {'true' if self.end else 'false'}"
        )
