import json
from typing import List

from python_tca2 import constants
from python_tca2.aelement import AlignmentElement
from python_tca2.alignment_suggestion import AlignmentSuggestion
from python_tca2.elementinfotobecompared import ElementInfoToBeCompared
from python_tca2.elementsinfo import ElementsInfo


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
        position: tuple[int, ...],
        alignment_suggestion: AlignmentSuggestion,
    ) -> ElementInfoToBeCompared:
        """Get the values of a cell in the comparison matrix.

        Retrieve or compute the ElementInfoToBeCompared object for a given
        position and step.

        Args:
            position: A list representing the current position in the matrix.
            alignment_suggestion: An AlignmentSuggestion defining the suggestions
                increments.

        Returns:
            A ElementInfoToBeCompared object containing comparison data for the
            given position and alignment_suggestion.
        """
        key = ",".join(
            [
                str(position[text_number] + 1)
                for text_number in range(constants.NUM_FILES)
            ]
            + [
                str(position[text_number] + alignment_suggestion[text_number])
                for text_number in range(constants.NUM_FILES)
            ]
        )

        if key not in self.comparison_matrix:
            self.comparison_matrix[key] = self.build_comparison_matrix_cell(
                nodes, position, alignment_suggestion
            )

        return self.comparison_matrix[key]

    def build_comparison_matrix_cell(
        self,
        nodes: tuple[List[AlignmentElement], ...],
        position: tuple[int, ...],
        alignment_suggestion: AlignmentSuggestion,
    ) -> ElementInfoToBeCompared:
        """
        Builds a comparison matrix cell for the given position and step.

        Args:
            position: A list representing the current position in the matrix.
            alignment_suggestion: An AlignmentSuggestion to consider from the current
                position.

        Returns:
            A ElementInfoToBeCompared object containing the comparison data and best
            path score.
        """
        element_info_to_be_compared = ElementInfoToBeCompared()
        element_info_to_be_compared.build_elementstobecompared(
            position,
            alignment_suggestion,
            nodes,
            self.elements_info,
        )

        return element_info_to_be_compared
