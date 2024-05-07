import json

from python_tca2.elementinfotobecompared import ElementInfoToBeCompared
from python_tca2.elementsinfo import ElementsInfo
from python_tca2.pathstep import PathStep


class CompareCells:
    def __init__(  # noqa: PLR0913
        self,
        elements_info: list[ElementsInfo],
        position: list[int],
        step: PathStep,
        nodes,
        anchor_word_list,
    ):
        self.element_info_to_be_compared = ElementInfoToBeCompared()
        self.element_info_to_be_compared.build_elementstobecompared(
            position, step, nodes, anchor_word_list, elements_info
        )
        self.best_path_score: float = -1.0

    def get_score(self):
        return self.element_info_to_be_compared.get_score()

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def to_json(self):
        return {
            "element_info_to_be_compared": self.element_info_to_be_compared.to_json(),
            "best_path_score": self.best_path_score,
        }
