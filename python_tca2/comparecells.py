import json

from python_tca2 import constants
from python_tca2.elementinfotobecompared import ElementInfoToBeCompared
from python_tca2.exceptions import EndOfAllTextsExceptionError, EndOfTextExceptionError


class CompareCells:
    def __init__(self, model, position, step):
        self.element_info_to_be_compared = ElementInfoToBeCompared()
        self.best_path_score: float = -1.0
        text_end_count = 0
        for text_number in range(constants.NUM_FILES):
            for x in range(
                position[text_number] + 1,
                position[text_number] + step.increment[text_number] + 1,
            ):
                try:
                    info = model.compare.elements_info[text_number].get_element_info(
                        model, x, text_number
                    )
                    self.element_info_to_be_compared.add(info, text_number)
                except EndOfTextExceptionError:
                    text_end_count += 1
                    break
        if text_end_count >= constants.NUM_FILES:
            raise EndOfAllTextsExceptionError()
        elif text_end_count > 0:
            raise EndOfTextExceptionError()

    def get_score(self):
        return self.element_info_to_be_compared.get_score()

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def to_json(self):
        return {
            "element_info_to_be_compared": self.element_info_to_be_compared.to_json(),
            "best_path_score": self.best_path_score,
        }
