import json
from typing import List

from python_tca2 import constants
from python_tca2.aelement import AlignmentElement
from python_tca2.anchorwordlist import AnchorWordList
from python_tca2.comparecells import CompareCell
from python_tca2.elementinfotobecompared import ElementInfoToBeCompared
from python_tca2.elementsinfo import ElementsInfo
from python_tca2.pathstep import PathStep


class Compare:
    def __init__(self) -> None:
        """Initialize the Compare class with anchor words and node elements.

        Attributes:
            elements_info: A list of ElementsInfo objects for each file.
            matrix: A dictionary to store comparison cells.
            best_path_scores: A dictionary to store the best path scores.
        """
        self.elements_info: List[ElementsInfo] = [
            ElementsInfo() for _ in range(constants.NUM_FILES)
        ]
        self.comparison_matrix: dict[str, CompareCell] = {}

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
        nodes: dict[int, List[AlignmentElement]],
        anchor_word_list: AnchorWordList,
        position: list[int],
        step: PathStep,
        best_path_scores: dict[str, float],
    ) -> CompareCell:
        """Retrieve or compute the CompareCell object for a given position and step.

        Args:
            position: A list representing the current position in the matrix.
            step: A PathStep object defining the step increments.

        Returns:
            A CompareCell object containing comparison data for the given position
            and step.
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
        nodes: dict[int, List[AlignmentElement]],
        anchor_word_list: AnchorWordList,
        position: list[int],
        step: PathStep,
        best_path_scores: dict[str, float],
    ) -> CompareCell:
        """
        Builds a comparison matrix cell for the given position and step.

        Args:
            position: A list representing the current position in the matrix.
            step: The step to take from the current position.

        Returns:
            A CompareCell object containing the comparison data and best path score.
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

        return CompareCell(
            element_info_to_be_compared=element_info_to_be_compared,
            best_path_score=best_path_scores[best_path_score_key],
        )

    def get_score(
        self, position: list[int], best_path_scores: dict[str, float]
    ) -> float:
        """Calculate and return the score for a given position.

        Args:
            position: A list of integers representing the position.

        Returns:
            The score as a float for the given position.
        """
        if any(pos < 0 for pos in position):
            return constants.BEST_PATH_SCORE_BAD

        best_path_score_key = ",".join(str(pos) for pos in position)
        return best_path_scores.get(
            best_path_score_key, constants.BEST_PATH_SCORE_NOT_CALCULATED
        )
