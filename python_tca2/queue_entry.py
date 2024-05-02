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
