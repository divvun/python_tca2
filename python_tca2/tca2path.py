from copy import deepcopy
from typing import List

from python_tca2 import constants
from python_tca2.pathstep import PathStep


class Tca2Path:
    """Represents a navigational path with steps and positional updates.

    Attributes:
        steps: A list of PathStep objects representing the path's steps.
        position: A list representing the current position in the path.
    """

    def __init__(self, initial_position: list[int]) -> None:
        self.steps: List[PathStep] = []
        self.position = initial_position

    def to_json(self):
        return {
            "steps": [step.to_json() for step in self.steps],
            "position": self.position,
        }

    def __eq__(self, path):
        return str(self) == str(path)

    def extend(self, step: PathStep) -> None:
        """Extend the current path with a cloned step and update positions.

        Args:
            step: The path step to be added and used for position updates.
        """
        self.steps.append(step.clone())
        for text_number in range(constants.NUM_FILES):
            self.position[text_number] += step.increment[text_number]

    def __str__(self):
        return (
            f"[{', '.join([str(step) for step in self.steps])}]->"
            + "{"
            + f"{self.position[0]},{self.position[1]}"
            + "}"
        )

    def clone(self):
        return deepcopy(self)

    def get_length_in_sentences(self):
        """Calculate the total number of sentences across all steps.

        Iterates through the steps and sums up the sentence increments for each
        text number to compute the total count.

        Returns:
            The total count of sentences.
        """
        return sum(
            step.increment[text_number]
            for step in self.steps
            for text_number in range(constants.NUM_FILES)
        )
