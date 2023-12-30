from copy import deepcopy

from python_tca2.alignment_utils import print_frame


class PathStep:
    def __init__(self, inc):
        print_frame()
        self.increment = inc

    def is11(self):
        print_frame()
        for t in range(len(self.increment)):
            if self.increment[t] != 1:
                return False
        return True

    def __str__(self):
        temp = "{"
        for t in range(len(self.increment)):
            if t > 0:
                temp += ","
            temp += str(self.increment[t])
        temp += "}"
        print_frame("__str__", temp)
        return temp

    def clone(self):
        print_frame()
        return deepcopy(self)
