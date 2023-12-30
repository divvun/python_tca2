from python_tca2.alignment_utils import print_frame


class Unaligned:
    def __init__(self):
        # print_frame()
        self.elements = [[], []]

    def pop(self, t):
        # print_frame()
        return self.elements[t].pop()

    def add(self, element, t):
        # print_frame()
        self.elements[t].append(element)
