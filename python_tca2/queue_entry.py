from typing import List

from python_tca2.alignment_utils import print_frame
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
