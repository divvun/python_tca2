from typing import List

from aelement import AElement
from link import Link

from corpustools import alignment


class AlignmentsEtc:
    def __init__(self):
        self.alignments: List[Link] = []  # 2006-11-20
        self.elements: List[List[AElement]] = [[] for _ in range(alignment.NUM_FILES)]
