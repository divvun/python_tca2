from python_tca2 import constants
from python_tca2.alignment_utils import print_frame
from python_tca2.bestpathscore import BestPathScore


class CompareMatrix:
    def __init__(self):
        print_frame()
        self.cells = {}
        self.best_path_scores = {}

    def get_score(self, model, position):
        outside = False
        for t in range(constants.NUM_FILES):
            if position[t] < 0:
                outside = True
                break

        if outside:
        print_frame()
            return constants.BEST_PATH_SCORE_BAD
        else:
            best_path_score_key = ",".join(str(pos) for pos in position)
            if best_path_score_key not in self.best_path_scores:
                return constants.BEST_PATH_SCORE_BAD
            else:
                print_frame(
                    "best_path_score_key in self.best_path_scores",
                    best_path_score_key,
                    self.best_path_scores[best_path_score_key].get_score(),
                )
                return self.best_path_scores[best_path_score_key].get_score()

    def set_score(self, position, score):
        print_frame()
        best_path_score_key = ""
        for t in range(constants.NUM_FILES):
            if t > 0:
                best_path_score_key += ","
            best_path_score_key += str(position[t])
        self.best_path_scores[best_path_score_key] = BestPathScore(score)

    def reset_best_path_scores(self):
        for key in self.best_path_scores.keys():
            print_frame("CompareMatrix.reset_best_path_scores: " + key)
            self.best_path_scores[key] = BestPathScore(
                constants.BEST_PATH_SCORE_NOT_CALCULATED
            )

    def to_string(self):
        print_frame()
        ret = ""
        key = ""
        it1 = self.cells.keySet().iterator()
        while it1.has_next():
            key = it1.next()
            ret += "(" + key + " : "
            ret += self.cells.get(key)
            ret += ")\n"

        it2 = self.best_path_scores.keySet().iterator()
        while it2.has_next():
            key = it2.next()
            ret += "(" + key + " : "
            ret += self.best_path_scores.get(key)
            ret += ")\n"

        return ret
