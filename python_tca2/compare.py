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
    def __init__(
        self, anchor_word_list: AnchorWordList, nodes: dict[int, List[AlignmentElement]]
    ) -> None:
        """Initialize the Compare class with anchor words and node elements.

        Args:
            anchor_word_list: The list of anchor words.
            nodes: A dictionary mapping integers to lists of elements.

        Attributes:
            anchor_word_list: Stores the provided anchor word list.
            nodes: Stores the provided node elements.
            elements_info: A list of ElementsInfo objects for each file.
            matrix: A dictionary to store comparison cells.
            best_path_scores: A dictionary to store the best path scores.
        """
        self.anchor_word_list = anchor_word_list
        self.nodes = nodes
        self.elements_info: List[ElementsInfo] = [
            ElementsInfo() for _ in range(constants.NUM_FILES)
        ]
        self.comparison_matrix: dict[str, CompareCell] = {}
        self.best_path_scores: dict[str, float] = {}

    def to_json(self) -> dict:
        return {
            "elements_info": [ei.to_json() for ei in self.elements_info],
            "matrix": {
                key: self.comparison_matrix[key].to_json()
                for key in sorted(self.comparison_matrix.keys())
            },
            "best_path_scores": self.best_path_scores,
        }

    def __str__(self) -> str:
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def get_cell_values(self, position: list[int], step: PathStep) -> CompareCell:
        """Retrieve or compute the CompareCells object for a given position and step.

        Args:
            position: A list representing the current position in the matrix.
            step: A PathStep object defining the step increments.

        Returns:
            A CompareCells object containing comparison data for the given position
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
        best_path_score_key = ",".join(
            [
                str(position[text_number] + step.increment[text_number])
                for text_number in range(constants.NUM_FILES)
            ]
        )

        if key not in self.comparison_matrix:
            element_info_to_be_compared = ElementInfoToBeCompared()
            element_info_to_be_compared.build_elementstobecompared(
                position,
                step,
                self.nodes,
                self.anchor_word_list,
                self.elements_info,
            )
            self.comparison_matrix[key] = CompareCell(
                element_info_to_be_compared=element_info_to_be_compared
            )

            if best_path_score_key in self.best_path_scores:
                temp = self.best_path_scores[best_path_score_key]
                self.comparison_matrix[key].best_path_score = temp
            else:
                self.comparison_matrix[key].best_path_score = (
                    constants.BEST_PATH_SCORE_BAD
                )

            self.best_path_scores[best_path_score_key] = self.comparison_matrix[
                key
            ].best_path_score

        return self.comparison_matrix[key]

    def get_score(self, position: list[int]) -> float:
        """Calculate and return the score for a given position.

        Args:
            position: A list of integers representing the position.

        Returns:
            The score as a float for the given position.

        Raises:
            SystemExit: If the position key is not found in best_path_scores.
        """
        if any(pos < 0 for pos in position):
            return constants.BEST_PATH_SCORE_BAD

        best_path_score_key = ",".join(str(pos) for pos in position)
        if best_path_score_key not in self.best_path_scores:
            raise SystemExit("best_path_score_key not in self.best_path_scores")
        else:
            return self.best_path_scores[best_path_score_key]

    def set_score(self, position: list[int], score: float) -> None:
        """Sets the score for a specific position in the best path scores.

        Args:
            position: A list representing the position in the path.
            score: The score to assign to the specified position.
        """
        best_path_score_key = ",".join(str(pos) for pos in position)
        self.best_path_scores[best_path_score_key] = score

    def reset_best_path_scores(self) -> None:
        """Reset all best path scores to the default uncalculated value.

        This method iterates through the keys in the best_path_scores dictionary
        and sets each value to the constant BEST_PATH_SCORE_NOT_CALCULATED.
        """
        for key in self.best_path_scores.keys():
            self.best_path_scores[key] = constants.BEST_PATH_SCORE_NOT_CALCULATED
