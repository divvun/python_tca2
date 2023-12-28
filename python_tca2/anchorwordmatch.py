class AnchorWordMatch:
    def __init__(self, i, ws):
        self.index = i
        self.words = ws

    def __str__(self):
        ret = []
        ret.append(
            str(self.index + 1)
        )  # +1 since we want anchor word entries numbered from 1 and upwards when they are displayed
        for word in self.words:
            ret.append(word)
        return " ".join(ret)
