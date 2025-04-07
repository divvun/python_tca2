import json

from python_tca2.elementinfotobecompared import ElementInfoToBeCompared


class CompareCell:
    def __init__(
        self,
        element_info_to_be_compared: ElementInfoToBeCompared,
        best_path_score: float = -1.0,
    ):
        self.element_info_to_be_compared = element_info_to_be_compared
        self.best_path_score = best_path_score

    def get_score(self):
        return self.element_info_to_be_compared.get_score()

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def to_json(self):
        return {
            "element_info_to_be_compared": self.element_info_to_be_compared.to_json(),
            "best_path_score": self.best_path_score,
        }
