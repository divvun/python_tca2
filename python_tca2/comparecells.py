from python_tca2 import constants
from python_tca2.elementinfotobecompared import ElementInfoToBeCompared
from python_tca2.exceptions import EndOfAllTextsExceptionError, EndOfTextExceptionError


class CompareCells:
    def __init__(self, model, position, step):
        self.element_info_to_be_compared = ElementInfoToBeCompared()
        self.best_path_score: float = -1.0
        text_end_count = 0
        for t in range(constants.NUM_FILES):
            for x in range(position[t] + 1, position[t] + step.increment[t] + 1):
                try:
                    info = model.compare.elements_info[t].get_element_info(model, x, t)
                    self.element_info_to_be_compared.add(info, t)
                except EndOfTextExceptionError:
                    print("CC EndOfTextException")
                    text_end_count += 1
                    break
        if text_end_count >= constants.NUM_FILES:
            print("1 cc")
            raise EndOfAllTextsExceptionError()
        elif text_end_count > 0:
            print("2 cc")
            raise EndOfTextExceptionError()
        print("3 cc")

    def get_score(self):
        return self.element_info_to_be_compared.get_score()

    def __str__(self):
        return (
            "CompareCells: "
            f"{self.element_info_to_be_compared}"
            f",\nbestPathScore: {self.best_path_score}\n"
        )

    def to_json(self):
        return {
            "element_info_to_be_compared": self.element_info_to_be_compared.to_json(),
            "best_path_score": self.best_path_score,
        }
