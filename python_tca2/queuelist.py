from typing import List

from python_tca2 import constants
from python_tca2.queue_entry import QueueEntry


class QueueList:
    def __init__(self):
        self.entry: List[QueueEntry] = []

    def empty(self) -> bool:
        return len(self.entry) == 0

    def add(self, queue_entry: QueueEntry):
        self.entry.append(queue_entry)

    def contains(self, queue_entry: QueueEntry) -> bool:
        for next_queue_entry in self.entry:
            if next_queue_entry.path == queue_entry.path:
                return True
        return False

    def remove(self, pos: List[int]):
        t = 0
        for queue_entry in self.entry:
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
        to_remove = []
        for queue_entry in self.entry:
            if queue_entry.removed:
                to_remove.append(queue_entry)

        for queue_entry in to_remove:
            self.entry.remove(queue_entry)
