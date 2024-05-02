from dataclasses import dataclass
from typing import List

from python_tca2.anchorwordhit import AnchorWordHit


@dataclass
class AnchorWordHits:
    hits: List[AnchorWordHit]

    def add(self, hit):
        self.hits.append(hit)
