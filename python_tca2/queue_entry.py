from copy import deepcopy

from python_tca2.alignment_utils import print_frame
from python_tca2.exceptions import (
    BlockedException,
    EndOfAllTextsException,
    EndOfTextException,
)
from python_tca2.path import Path


class QueueEntry:
    def __init__(self, position, score):
        print_frame("__init__")
        self.path = Path(position)
        self.score = score
        self.removed = False
        self.end = False

    def make_longer_path(self, model, new_step):
        print_frame("make_longer_path")
        ret_queue_entry = deepcopy(self)
        new_score = self.try_step(model, new_step)
        ret_queue_entry.score = new_score
        ret_queue_entry.path.extend(new_step)
        if ret_queue_entry.score > model.compare.get_score(
            model, ret_queue_entry.path.position
        ):
            model.compare.set_score(
                ret_queue_entry.path.position, ret_queue_entry.score
            )
            return ret_queue_entry
        else:
            ret_queue_entry.path = None
            return ret_queue_entry

    def try_step(self, model, step):
        print_frame("try_step")
        step_score = 0.0
        try:
            step_score = self.get_step_score(model, self.path.position, step)
        except EndOfAllTextsException as e:
            print_frame("EndOfAllTextsException")
            raise e
        except EndOfTextException as e:
            print_frame("EndOfTextException")
            raise e
        except BlockedException as e:
            print_frame("BlockedException")
            raise e
        return self.score + step_score

    def get_step_score(self, model, position, step):
        print_frame("get_step_score")
        try:
            cell = model.compare.get_cell_values(model, position, step)
            return cell.get_score()
        except EndOfAllTextsException as e:
            raise e
        except EndOfTextException as e:
            raise e

    def remove(self):
        print_frame("remove")
        self.removed = True
