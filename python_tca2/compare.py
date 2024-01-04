from typing import List

from python_tca2 import constants
from python_tca2.comparecells import CompareCells
from python_tca2.comparematrix import CompareMatrix
from python_tca2.elementsinfo import ElementsInfo
from python_tca2.pathstep import PathStep


class Compare:
    def __init__(self):
        # print_frame()
        self.elements_info: List[ElementsInfo] = [
            ElementsInfo() for _ in range(constants.NUM_FILES)
        ]
        self.matrix: CompareMatrix = CompareMatrix()
        self.step_list: List[PathStep] = []

        self.create_step_list()

    def __str__(self):
        # print_frame()
        temp = "{\nCompare: {\n"
        temp += "elementsInfo: [\n"
        temp += ",\n".join(
            f"{self.elements_info[t]}" for t in range(constants.NUM_FILES)
        )
        temp += "],\nmatrix: {\n"
        temp += f"{self.matrix}"
        temp += "},\n"
        temp += f"stepList: [\n{',\n'.join(str(step) for step in self.step_list)}\n]\n"
        temp += "}\n}\n\n"

        return temp

    def get_cell_values(self, model, position, step):
        # print_frame()
        key = ",".join(
            [str(position[t] + 1) for t in range(constants.NUM_FILES)]
            + [str(position[t] + step.increment[t]) for t in range(constants.NUM_FILES)]
        )
        best_path_score_key = ",".join(
            [str(position[t] + step.increment[t]) for t in range(constants.NUM_FILES)]
        )

        if key not in self.matrix.cells:
            # Lag en ny celle
            self.matrix.cells[key] = CompareCells(model, position, step)

            # Hvis best_path_score_key finnes i best_path_scores, så kopierer vi
            if best_path_score_key in self.matrix.best_path_scores:
                temp = self.matrix.best_path_scores[best_path_score_key]
                self.matrix.cells[key].best_path_score = temp
            else:
                self.matrix.cells[
                    key
                ].best_path_score = constants.BEST_PATH_SCORE_NOT_CALCULATED

            self.matrix.best_path_scores[best_path_score_key] = self.matrix.cells[
                key
            ].best_path_score

        return self.matrix.cells[key]

    @staticmethod
    def int_to_base(i, base):
        # print_frame()
        if i == 0:
            return "0"
        digits = []
        while i:
            digits.append(int(i % base))
            i //= base
        digits = digits[::-1]
        return "".join(map(str, digits))

    def create_step_list(self):
        # print_frame()
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

            for t in range(constants.NUM_FILES):
                increment[t] = constants.MIN_NUM_TRY + int(comb_string[t], range_val)
                total += increment[t]
                minimum = min(minimum, increment[t])
                maximum = max(maximum, increment[t])

            if (
                maximum > 0
                and maximum - minimum <= constants.MAX_DIFF_TRY
                and total <= constants.MAX_TOTAL_TRY
            ):
                self.step_list.append(PathStep(increment))

    def get_score(self, position):
        # print_frame()
        return self.matrix.get_score(position)

    def set_score(self, position, score):
        # print_frame()
        self.matrix.set_score(position, score)

    def reset_best_path_scores(self):
        # print_frame()
        self.matrix.reset_best_path_scores()
