from dataclasses import dataclass

from python_tca2.anchorwordhit import AnchorWordHit


@dataclass
class AnchorWordHits:
    hits: list[AnchorWordHit]
