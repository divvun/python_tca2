import json
from dataclasses import asdict
from typing import List

from python_tca2 import constants
from python_tca2.anchorwordlist import AnchorWordList
from python_tca2.comparecells import CompareCells
from python_tca2.elementsinfo import ElementsInfo
from python_tca2.pathstep import PathStep


class Compare:
    def __init__(self, anchor_word_list: AnchorWordList, nodes):
        self.anchor_word_list = anchor_word_list
        self.nodes = nodes
        self.elements_info: List[ElementsInfo] = [
            ElementsInfo() for _ in range(constants.NUM_FILES)
        ]
        self.matrix: dict[str, CompareCells] = {}
        self.best_path_scores: dict[str, float] = {}

        self.step_list: List[PathStep] = []

        self.create_step_list()

    def to_json(self):
        return {
            "elements_info": [ei.to_json() for ei in self.elements_info],
            "matrix": {
                key: self.matrix[key].to_json() for key in sorted(self.matrix.keys())
            },
            "step_list": [asdict(step) for step in self.step_list],
            "best_path_scores": self.best_path_scores,
        }

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def get_cell_values(self, position, step):
        key = ",".join(
            [
                str(position[text_number] + 1)
                for text_number in range(constants.NUM_FILES)
            ]
            + [
                str(position[text_number] + step.increment[text_number])
                for text_number in range(constants.NUM_FILES)
            ]
        )
        best_path_score_key = ",".join(
            [
                str(position[text_number] + step.increment[text_number])
                for text_number in range(constants.NUM_FILES)
            ]
        )

        if key not in self.matrix:
            self.matrix[key] = CompareCells(
                self.elements_info,
                position,
                step,
                self.nodes,
                self.anchor_word_list,
            )

            if best_path_score_key in self.best_path_scores:
                temp = self.best_path_scores[best_path_score_key]
                self.matrix[key].best_path_score = temp
            else:
                self.matrix[key].best_path_score = constants.BEST_PATH_SCORE_BAD

            self.best_path_scores[best_path_score_key] = self.matrix[
                key
            ].best_path_score

        return self.matrix[key]

    @staticmethod
    def int_to_base(i, base):
        if i == 0:
            return "0"
        digits = []
        while i:
            digits.append(int(i % base))
            i //= base
        digits = digits[::-1]
        return "".join(map(str, digits))

    def create_step_list(self):
        range_val = constants.MAX_NUM_TRY - constants.MIN_NUM_TRY + 1
        limit = 1
        for _ in range(constants.NUM_FILES):
            limit *= range_val

        for i in range(limit):
            increment = [0] * constants.NUM_FILES

            comb_string = self.int_to_base(limit + i, range_val)[
                1 : constants.NUM_FILES + 1
            ]
            minimum = constants.MAX_NUM_TRY + 1
            maximum = constants.MIN_NUM_TRY - 1
            total = 0

            for text_number in range(constants.NUM_FILES):
                increment[text_number] = constants.MIN_NUM_TRY + int(
                    comb_string[text_number], range_val
                )
                total += increment[text_number]
                minimum = min(minimum, increment[text_number])
                maximum = max(maximum, increment[text_number])

            if (
                maximum > 0
                and maximum - minimum <= constants.MAX_DIFF_TRY
                and total <= constants.MAX_TOTAL_TRY
            ):
                self.step_list.append(PathStep(increment))

    def get_score(self, position):
        if any(pos < 0 for pos in position):
            return constants.BEST_PATH_SCORE_BAD

        best_path_score_key = ",".join(str(pos) for pos in position)
        if best_path_score_key not in self.best_path_scores:
            raise SystemExit("best_path_score_key not in self.best_path_scores")
        else:
            return self.best_path_scores[best_path_score_key]

    def set_score(self, position, score):
        best_path_score_key = ",".join(str(pos) for pos in position)
        self.best_path_scores[best_path_score_key] = score

    def reset_best_path_scores(self):
        for key in self.best_path_scores.keys():
            self.best_path_scores[key] = constants.BEST_PATH_SCORE_NOT_CALCULATED
