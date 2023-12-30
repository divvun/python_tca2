from typing import List

from python_tca2.alignment_utils import print_frame
from python_tca2.anchorwordhit import AnchorWordHit


class AnchorWordHits:
    def __init__(self):
        # print_frame()
        self.hits: List[AnchorWordHit] = []

    def add(self, hit):
        # print_frame()
        self.hits.append(hit)

    def __str__(self):
        # print_frame()
        ret = "["
        for i, hit in enumerate(self.hits):
            if i > 0:
                ret += ","
            ret += str(hit)
        ret += "]"
        return ret
