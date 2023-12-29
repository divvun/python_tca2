from python_tca2.path import Path


class QueueEntry:
    def __init__(self, position, score):
        self.path = Path(position)
        self.score = score
        self.removed = False
        self.end = False

    def make_longer_path(self, model, new_step):
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
