import json


class AnchorWordMatch:
    def __init__(self, i, ws):
        self.index = i
        self.words = ws

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def to_json(self):
        return {
            "index": self.index,
            "words": self.words,
        }
