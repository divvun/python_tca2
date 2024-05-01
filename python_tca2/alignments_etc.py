from collections import defaultdict

from python_tca2.aelement import AElement
from python_tca2.link import Link


class AlignmentsEtc:
    def __init__(self):
        self.alignments: list[Link] = []
        self.elements: defaultdict[int, list[AElement]] = defaultdict(list)
