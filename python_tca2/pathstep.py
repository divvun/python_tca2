from dataclasses import dataclass


@dataclass
class PathStep:
    increment: tuple[int, ...]
