from typing import List

from python_tca2 import constants
from python_tca2.aelement import AElement
from python_tca2.alignment_utils import print_frame
from python_tca2.link import Link


class AlignmentsEtc:
    def __init__(self):
        # print_frame("__init__")
        self.alignments: List[Link] = []
        self.elements: List[List[AElement]] = [[] for _ in range(constants.NUM_FILES)]
