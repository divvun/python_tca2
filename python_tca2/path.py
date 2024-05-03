from typing import List

from python_tca2 import constants
from python_tca2.pathstep import PathStep


class Path:
    def __init__(self, initial_position):
        self.steps: List[PathStep] = []
        self.position = initial_position

    def to_json(self):
        return {
            "steps": [step.to_json() for step in self.steps],
            "position": self.position,
        }

    def __eq__(self, path):
        return str(self) == str(path)

    def extend(self, step):
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
        copy = Path(self.position.copy())
        copy.steps = [step.clone() for step in self.steps]
        return copy

    def get_length_in_sentences(self):
        count = 0
        for step in self.steps:
            for text_number in range(constants.NUM_FILES):
                count += step.increment[text_number]
        return count
