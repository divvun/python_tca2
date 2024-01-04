from typing import Dict, List

from python_tca2 import constants
from python_tca2.comparecells import CompareCells


class CompareMatrix:
    def __init__(self):
        # print_frame()
        self.cells: Dict[str, CompareCells] = {}
        self.best_path_scores: Dict[str, float] = {}

    def __str__(self):
        cells = "\n".join([f"{key}: {self.cells[key]}" for key in self.cells.keys()])
        bp = "\n".join(
            [
                f"{key}: {self.best_path_scores[key]}"
                for key in self.best_path_scores.keys()
            ]
        )
        return (
            "CompareMatrix: {\n"
            + "cells: [\n"
            + cells
            + "]\nbestPathScores: [\n"
            + bp
            + "]\n}"
        )

    def get_score(self, position) -> float:
        # print_frame()
        if any(pos < 0 for pos in position):
            # raise SystemExit("outside")
            # print_frame("outside", position)
            return constants.BEST_PATH_SCORE_BAD

        best_path_score_key = ",".join(str(pos) for pos in position)
        if best_path_score_key not in self.best_path_scores:
            raise SystemExit("best_path_score_key not in self.best_path_scores")
        else:
            # print_frame(
            #     "best_path_score_key in self.best_path_scores",
            #     best_path_score_key,
            #     self.best_path_scores[best_path_score_key].get_score(),
            # )
            return self.best_path_scores[best_path_score_key]

    def set_score(self, position: List[int], score: float):
        best_path_score_key = ",".join(str(pos) for pos in position)
        self.best_path_scores[best_path_score_key] = score
        # print_frame(best_path_score_key, score, self.best_path_scores[best_path_score_key])

    def reset_best_path_scores(self):
        for key in self.best_path_scores.keys():
            # print_frame("CompareMatrix.reset_best_path_scores: " + key)
            self.best_path_scores[key] = constants.BEST_PATH_SCORE_NOT_CALCULATED
