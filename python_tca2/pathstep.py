from copy import deepcopy
from dataclasses import dataclass


@dataclass
class PathStep:
    increment: tuple[int, ...]

    def clone(self):
        return deepcopy(self)
