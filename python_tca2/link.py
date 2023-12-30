from python_tca2 import constants
from python_tca2.alignment_utils import print_frame


class Link:
    def __init__(self):
        print_frame()
        self.alignment_number = -1
        self.element_numbers = [set() for _ in range(constants.NUM_FILES)]

    def __str__(self):
        print_frame()
        str_ = "("
        for t in range(constants.NUM_FILES):
            if t > 0:
                str_ += ";"
            str_ += "size=" + str(len(self.element_numbers[t]))
            for el in self.element_numbers[t]:
                str_ += ",el=" + str(el)
        str_ += ")"
        str_ += " alignment number " + str(self.alignment_number)
        return str_
