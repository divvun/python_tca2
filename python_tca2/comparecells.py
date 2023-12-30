from python_tca2 import constants
from python_tca2.alignment_utils import print_frame
from python_tca2.elementinfotobecompared import ElementInfoToBeCompared
from python_tca2.exceptions import EndOfAllTextsException, EndOfTextException


class CompareCells:
    def __init__(self, model, position, step):
        print_frame()
        self.element_info_to_be_compared = ElementInfoToBeCompared(model)
        text_end_count = 0
        for t in range(constants.NUM_FILES):
            for x in range(position[t] + 1, position[t] + step.increment[t] + 1):
                try:
                    info = model.compare.elements_info[t].get_element_info(model, x, t)
                    self.element_info_to_be_compared.add(info, t)
                except EndOfTextException:
                    text_end_count += 1
                    break
        if text_end_count >= constants.NUM_FILES:
            raise EndOfAllTextsException()
        elif text_end_count > 0:
            raise EndOfTextException()

    def get_score(self):
        print_frame()
        return self.element_info_to_be_compared.get_score()

    def __str__(self):
        print_frame()
        return (
            "CompareCells' toString. score="
            + str(self.element_info_to_be_compared.get_score())
            + ", best path score="
            + str(self.best_path_score.get_score())
        )
