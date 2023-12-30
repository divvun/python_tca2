from python_tca2.alignment_utils import print_frame


class AnchorWordMatch:
    def __init__(self, i, ws):
        # print_frame()
        self.index = i
        self.words = ws

    def __str__(self):
        # print_frame()
        ret = []
        ret.append(str(self.index + 1))
        for word in self.words:
            ret.append(word)
        return " ".join(ret)
