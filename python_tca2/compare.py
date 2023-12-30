from python_tca2 import constants
from python_tca2.alignment_utils import print_frame
from python_tca2.bestpathscore import BestPathScore
from python_tca2.comparecells import CompareCells
from python_tca2.comparematrix import CompareMatrix
from python_tca2.elementsinfo import ElementsInfo
from python_tca2.exceptions import EndOfAllTextsException, EndOfTextException
from python_tca2.pathstep import PathStep


class Compare:
    def __init__(self):
        print_frame("__init__")
        self.elements_info = [ElementsInfo() for _ in range(constants.NUM_FILES)]
        self.matrix = CompareMatrix()
        self.step_list = []

        for t in range(constants.NUM_FILES):
            self.elements_info[t] = ElementsInfo()

        self.create_step_list()

    def get_cell_values(self, model, position, step):
        print_frame("get_cell_values")
        key = ""
        best_path_score_key = ""

        for t in range(constants.NUM_FILES):
            if t > 0:
                key += ","
            key += str(position[t] + 1)

        key += ","

        for t in range(constants.NUM_FILES):
            if t > 0:
                key += ","
                best_path_score_key += ","
            key += str(position[t] + 1 + step.increment[t] - 1)
            best_path_score_key += str(position[t] + 1 + step.increment[t] - 1)

        if key not in self.matrix.cells:
            try:
                self.matrix.cells[key] = CompareCells(model, position, step)
            except EndOfAllTextsException as e:
                raise e
            except EndOfTextException as e:
                raise e

            if best_path_score_key in self.matrix.best_path_scores:
                temp = self.matrix.best_path_scores[best_path_score_key]
                self.matrix.cells[key].best_path_score = temp
            else:
                self.matrix.cells[key].best_path_score = BestPathScore()

            self.matrix.best_path_scores[best_path_score_key] = self.matrix.cells[
                key
            ].best_path_score

        return self.matrix.cells[key]

    @staticmethod
    def int_to_base(i, base):
        print_frame("int_to_base")
        if i == 0:
            return "0"
        digits = []
        while i:
            digits.append(int(i % base))
            i //= base
        digits = digits[::-1]
        return "".join(map(str, digits))

    def create_step_list(self):
        print_frame("create_step_list")
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
        print_frame("get_score")
        return self.matrix.get_score(position)

    def set_score(self, position, score):
        print_frame("set_score")
        self.matrix.set_score(position, score)

    def reset_best_path_scores(self):
        print_frame("reset_best_path_scores")
        print_frame("reset_best_path_scores")
        self.matrix.reset_best_path_scores()
