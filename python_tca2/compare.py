import json
from typing import List

from python_tca2 import constants
from python_tca2.aelement import AlignmentElement
from python_tca2.anchorwordlist import AnchorWordList
from python_tca2.elementinfotobecompared import ElementInfoToBeCompared
from python_tca2.elementsinfo import ElementsInfo
from python_tca2.pathstep import PathStep


class Compare:
    def __init__(self) -> None:
        """Initialize the Compare class with anchor words and node elements.

        Attributes:
            elements_info: A list of ElementsInfo objects for each file.
            matrix: A dictionary to store comparison cells.
        """
        self.elements_info: List[ElementsInfo] = [
            ElementsInfo() for _ in range(constants.NUM_FILES)
        ]
        self.comparison_matrix: dict[str, ElementInfoToBeCompared] = {}

    def to_json(self) -> dict:
        return {
            "elements_info": [ei.to_json() for ei in self.elements_info],
            "matrix": {
                key: self.comparison_matrix[key].to_json()
                for key in sorted(self.comparison_matrix.keys())
            },
        }

    def __str__(self) -> str:
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def get_cell_values(
        self,
        nodes: tuple[List[AlignmentElement], ...],
        anchor_word_list: AnchorWordList,
        position: list[int],
        step: PathStep,
        best_path_scores: dict[str, float],
    ) -> ElementInfoToBeCompared:
        """Get the values of a cell in the comparison matrix.

        Retrieve or compute the ElementInfoToBeCompared object for a given
        position and step.

        Args:
            position: A list representing the current position in the matrix.
            step: A PathStep object defining the step increments.

        Returns:

            A ElementInfoToBeCompared object containing comparison data for the
            given position and step.
        """
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

        if key not in self.comparison_matrix:
            self.comparison_matrix[key] = self.build_comparison_matrix_cell(
                nodes, anchor_word_list, position, step, best_path_scores
            )

        return self.comparison_matrix[key]

    def build_comparison_matrix_cell(
        self,
        nodes: tuple[List[AlignmentElement], ...],
        anchor_word_list: AnchorWordList,
        position: list[int],
        step: PathStep,
        best_path_scores: dict[str, float],
    ) -> ElementInfoToBeCompared:
        """
        Builds a comparison matrix cell for the given position and step.

        Args:
            position: A list representing the current position in the matrix.
            step: The step to take from the current position.

        Returns:
            A ElementInfoToBeCompared object containing the comparison data and best
            path score.
        """
        element_info_to_be_compared = ElementInfoToBeCompared()
        element_info_to_be_compared.build_elementstobecompared(
            position,
            step,
            nodes,
            anchor_word_list,
            self.elements_info,
        )

        best_path_score_key = ",".join(
            [
                str(position[text_number] + step.increment[text_number])
                for text_number in range(constants.NUM_FILES)
            ]
        )
        if best_path_scores.get(best_path_score_key) is None:
            best_path_scores[best_path_score_key] = (
                constants.BEST_PATH_SCORE_NOT_CALCULATED
            )
        element_info_to_be_compared.best_path_score = best_path_scores[
            best_path_score_key
        ]
        element_info_to_be_compared.best_path_score_key = best_path_score_key
        return element_info_to_be_compared
