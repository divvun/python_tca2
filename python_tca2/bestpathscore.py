from python_tca2 import constants
from python_tca2.alignment_utils import print_frame


class BestPathScore:
    def __init__(self, score=constants.BEST_PATH_SCORE_NOT_CALCULATED):
        # print_frame()
        self.score = score

    def get_score(self):
        # print_frame()
        return self.score

    def __str__(self):
        # print_frame()
        return str(self.score)
