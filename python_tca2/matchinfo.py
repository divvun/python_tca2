from python_tca2.alignment_utils import print_frame


class MatchInfo:
    def __init__(self, model):
        print_frame("__init__")
        self.model = model
        self.displayableList = []
