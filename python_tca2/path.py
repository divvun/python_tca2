import json
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
        for t in range(constants.NUM_FILES):
            self.position[t] += step.increment[t]

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def clone(self):
        copy = Path(self.position.copy())
        copy.steps = [step.clone() for step in self.steps]
        return copy

    def get_length_in_sentences(self):
        count = 0
        for step in self.steps:
            for t in range(constants.NUM_FILES):
                count += step.increment[t]
        return count
