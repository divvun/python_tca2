from dataclasses import dataclass
from typing import List

from python_tca2.queue_entry import QueueEntry


@dataclass
class QueueList:
    entries: List[QueueEntry]

    def empty(self) -> bool:
        return len(self.entries) == 0

    def add(self, queue_entry: QueueEntry):
        self.entries.append(queue_entry)

    def contains(self, queue_entry: QueueEntry) -> bool:
        return queue_entry in self.entries

    def remove(self, pos: List[int]):
        for queue_entry in self.entries:
            if queue_entry.has_hit(pos):
                queue_entry.remove()

    def remove_for_real(self):
        to_remove = [queue_entry for queue_entry in self.entries if queue_entry.removed]

        for queue_entry in to_remove:
            self.entries.remove(queue_entry)
