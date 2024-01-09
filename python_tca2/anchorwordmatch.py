class AnchorWordMatch:
    def __init__(self, i, ws):
        self.index = i
        self.words = ws

    def __str__(self):
        ret = []
        ret.append(str(self.index + 1))
        for word in self.words:
            ret.append(word)
        return " ".join(ret)

    def to_json(self):
        return {
            "index": self.index,
            "words": self.words,
        }
