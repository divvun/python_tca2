from typing import List

from python_tca2.anchorwordhit import AnchorWordHit


class AnchorWordHits:
    def __init__(self):
        self.hits: List[AnchorWordHit] = []

    def add(self, hit):
        self.hits.append(hit)

    def __str__(self):
        ret = "{\nAnchorwordHits: ["
        for i, hit in enumerate(self.hits):
            if i > 0:
                ret += ","
            ret += str(hit)
        ret += "]\n}"
        return ret
