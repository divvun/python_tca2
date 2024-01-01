from typing import List

from python_tca2 import constants
from python_tca2.alignment_utils import print_frame
from python_tca2.queue_entry import QueueEntry


class QueueList:
    def __init__(self):
        self.entry: List[QueueEntry] = []

    def empty(self) -> bool:
        return len(self.entry) == 0

    def add(self, queue_entry: QueueEntry):
        # print_frame()
        self.entry.append(queue_entry)

    def contains(self, queue_entry: QueueEntry) -> bool:
        # print_frame()
        for next_queue_entry in self.entry:
            if next_queue_entry.path == queue_entry.path:
                return True
        return False

    def remove(self, pos: List[int]):
        # print_frame(len(self.entry))
        debug = False
        t = 0
        for queue_entry in self.entry:
            if debug:
                print_frame(f">>> remove() entry {queue_entry}")
            hit = False
            current = list(queue_entry.path.position)
            current_ix = len(queue_entry.path.steps) - 1
            done = False
            while not done:
                if debug:
                    print_frame(
                        ">>> remove() current",
                        current,
                        "pos",
                        pos,
                        "current_ix",
                        current_ix,
                    )
                hope = True
                for t in range(constants.NUM_FILES):
                    if current[t] < pos[t]:
                        hope = False
                        break
                if hope:
                    if debug:
                        print_frame(">>> remove() hope")
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
                        if debug:
                            print_frame(">>> remove() hope but no current_ix")
                        done = True
                else:
                    if debug:
                        print_frame(">>> remove() no hope")
                    done = True

            if hit:
                queue_entry.remove()
                if debug:
                    print_frame(">>> hit. mark for removal entry", queue_entry, "\n")

        # print_frame(len(self.entry))

    def remove_for_real(self):
        # print_frame()
        to_remove = []
        for queue_entry in self.entry:
            if queue_entry.removed:
                to_remove.append(queue_entry)

        for queue_entry in to_remove:
            self.entry.remove(queue_entry)
