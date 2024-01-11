import json
from typing import Dict, List

from python_tca2 import constants
from python_tca2.comparecells import CompareCells


class CompareMatrix:
    def __init__(self):
        self.cells: Dict[str, CompareCells] = {}
        self.best_path_scores: Dict[str, float] = {}

    def to_json(self):
        return {
            "cells": {
                key: self.cells[key].to_json() for key in sorted(self.cells.keys())
            },
            "best_path_scores": self.best_path_scores,
        }

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def get_score(self, position) -> float:
        if any(pos < 0 for pos in position):
            # raise SystemExit("outside")

            return constants.BEST_PATH_SCORE_BAD

        best_path_score_key = ",".join(str(pos) for pos in position)
        if best_path_score_key not in self.best_path_scores:
            raise SystemExit("best_path_score_key not in self.best_path_scores")
        else:
            return self.best_path_scores[best_path_score_key]

    def set_score(self, position: List[int], score: float):
        best_path_score_key = ",".join(str(pos) for pos in position)
        self.best_path_scores[best_path_score_key] = score

    def reset_best_path_scores(self):
        for key in self.best_path_scores.keys():
            self.best_path_scores[key] = constants.BEST_PATH_SCORE_NOT_CALCULATED
