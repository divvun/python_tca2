import json
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
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def to_json(self):
        return {
            "path": self.path.to_json() if self.path is not None else None,
            "score": self.score,
            "removed": self.removed,
            "end": self.end,
        }
