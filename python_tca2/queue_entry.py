from copy import deepcopy

from python_tca2.alignment_utils import print_frame
from python_tca2.exceptions import (
    BlockedExceptionError,
    EndOfAllTextsExceptionError,
    EndOfTextExceptionError,
)
from python_tca2.path import Path


class QueueEntry:
    def __init__(self, position, score):
        print_frame()
        self.path = Path(position)
        self.score = score
        self.removed = False
        self.end = False

    def make_longer_path(self, model, new_step):
        print_frame()
        ret_queue_entry = deepcopy(self)
        try:
            new_score = self.try_step(model, new_step)
        except EndOfAllTextsExceptionError as e:
            raise e
        except EndOfTextExceptionError as e:
            raise e
        except BlockedExceptionError as e:
            raise e

        ret_queue_entry.score = new_score
        ret_queue_entry.path.extend(new_step)
        if ret_queue_entry.score > model.compare.get_score(
            ret_queue_entry.path.position
        ):
            model.compare.set_score(
                ret_queue_entry.path.position, ret_queue_entry.score
            )
            return ret_queue_entry
        else:
            ret_queue_entry.path = None
            return ret_queue_entry

    def try_step(self, model, step):
        print_frame()
        step_score = 0.0
        try:
            step_score = self.get_step_score(model, self.path.position, step)
        except EndOfAllTextsExceptionError as e:
            print_frame("EndOfAllTextsException")
            raise e
        except EndOfTextExceptionError as e:
            print_frame("EndOfTextException")
            raise e
        except BlockedExceptionError as e:
            print_frame("BlockedException")
            raise e
        return self.score + step_score

    def get_step_score(self, model, position, step):
        print_frame()
        try:
            cell = model.compare.get_cell_values(model, position, step)
            return cell.get_score()
        except EndOfAllTextsExceptionError as e:
            raise e
        except EndOfTextExceptionError as e:
            raise e

    def remove(self):
        print_frame()
        self.removed = True
