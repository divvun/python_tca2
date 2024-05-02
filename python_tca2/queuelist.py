from dataclasses import dataclass
from typing import List

from python_tca2 import constants
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
        t = 0
        for queue_entry in self.entries:
            hit = False
            current = list(queue_entry.path.position)
            current_ix = len(queue_entry.path.steps) - 1
            done = False
            while not done:
                hope = True
                for t in range(constants.NUM_FILES):
                    if current[t] < pos[t]:
                        hope = False
                        break
                if hope:
                    eq = True
                    for t in range(constants.NUM_FILES):
                        if current[t] != pos[t]:
                            eq = False
                            break
                    if eq:
                        hit = True
                        done = True
                    elif current_ix >= 0:
                        for t in range(constants.NUM_FILES):
                            current[t] -= queue_entry.path.steps[current_ix].increment[
                                t
                            ]
                        current_ix -= 1
                    else:
                        done = True
                else:
                    done = True

            if hit:
                queue_entry.remove()

    def remove_for_real(self):
        to_remove = [queue_entry for queue_entry in self.entries if queue_entry.removed]

        for queue_entry in to_remove:
            self.entries.remove(queue_entry)
