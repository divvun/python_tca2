from copy import deepcopy
from dataclasses import dataclass


@dataclass
class PathStep:
    increment: list[int]

    def is11(self):
        return all(i == 1 for i in self.increment)

    def clone(self):
        return deepcopy(self)
