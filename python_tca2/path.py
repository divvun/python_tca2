from typing import List

from python_tca2 import constants
from python_tca2.alignment_utils import print_frame
from python_tca2.pathstep import PathStep


class Path:
    def __init__(self, initial_position):
        print_frame("__init__")
        self.steps: List[PathStep] = []
        self.position = initial_position

    def __eq__(self, path):
        print_frame("__eq__")
        return str(self) == str(path)

    def extend(self, step):
        print_frame("extend")
        self.steps.append(step.clone())
        for t in range(constants.NUM_FILES):
            self.position[t] += step.increment[t]

    def __str__(self):
        print_frame("__str__")
        temp = "["
        first = True
        for step in self.steps:
            if not first:
                temp += ", "
            temp += "{"
            for t in range(constants.NUM_FILES):
                if t > 0:
                    temp += ","
                temp += str(step.increment[t])
            temp += "}"
            first = False
        temp += "]->"
        temp += "{"
        for t in range(constants.NUM_FILES):
            if t > 0:
                temp += ","
            temp += str(self.position[t])
        temp += "}"
        return temp

    def clone(self):
        print_frame("clone")
        copy = Path(self.position.copy())
        copy.steps = [step.clone() for step in self.steps]
        return copy

    def get_length_in_sentences(self):
        print_frame("get_length_in_sentences")
        count = 0
        for step in self.steps:
            for t in range(constants.NUM_FILES):
                count += step.increment[t]
        return count
