from dataclasses import dataclass


@dataclass
class AnchorWordHit:
    index: int
    element_number: int
    pos: int
    word: str
