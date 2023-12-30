from python_tca2 import constants
from python_tca2.alignment_utils import print_frame


class Aligned:
    def __init__(self):
        # print_frame()
        self.elements = [[] for _ in range(constants.NUM_FILES)]
        self.alignments = []

    def pickup(self, value_got):
        # print_frame()
        if value_got is not None:
            self.alignments.extend(value_got.alignments)
            for t in range(constants.NUM_FILES):
                for i in range(len(value_got.elements[t])):
                    self.elements[t].add(value_got.elements[t][i])
