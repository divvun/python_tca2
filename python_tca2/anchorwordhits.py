import json
from typing import List

from python_tca2.anchorwordhit import AnchorWordHit


class AnchorWordHits:
    def __init__(self):
        self.hits: List[AnchorWordHit] = []

    def add(self, hit):
        self.hits.append(hit)

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def to_json(self):
        return [hit.to_json() for hit in self.hits]
