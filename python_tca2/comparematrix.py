from typing import Dict, List

from python_tca2 import constants
from python_tca2.bestpathscore import BestPathScore
from python_tca2.comparecells import CompareCells


class CompareMatrix:
    def __init__(self):
        # print_frame()
        self.cells: Dict[str, CompareCells] = {}
        self.best_path_scores: Dict[str, BestPathScore] = {}

    def get_score(self, position) -> float:
        # print_frame()
        if any(pos < 0 for pos in position):
            # raise SystemExit("outside")
            # print_frame("outside", position)
            return constants.BEST_PATH_SCORE_BAD
        else:
            best_path_score_key = ",".join(str(pos) for pos in position)
            if best_path_score_key not in self.best_path_scores:
                raise SystemExit("best_path_score_key not in self.best_path_scores")
            else:
                # print_frame(
                #     "best_path_score_key in self.best_path_scores",
                #     best_path_score_key,
                #     self.best_path_scores[best_path_score_key].get_score(),
                # )
                return self.best_path_scores[best_path_score_key].get_score()

    def set_score(self, position: List[int], score: float):
        # print_frame()
        best_path_score_key = ",".join(str(pos) for pos in position)
        self.best_path_scores[best_path_score_key] = BestPathScore(score)

    def reset_best_path_scores(self):
        for key in self.best_path_scores.keys():
            # print_frame("CompareMatrix.reset_best_path_scores: " + key)
            self.best_path_scores[key] = BestPathScore(
                constants.BEST_PATH_SCORE_NOT_CALCULATED
            )

    def to_string(self) -> str:
        # print_frame()
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
