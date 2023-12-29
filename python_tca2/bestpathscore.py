from python_tca2 import constants


class BestPathScore:
    def __init__(self, score=constants.BEST_PATH_SCORE_NOT_CALCULATED):
        self.score = score

    def get_score(self):
        return self.score

    def __str__(self):
        return str(self.score)
