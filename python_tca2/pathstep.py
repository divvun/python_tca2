from copy import deepcopy


class PathStep:
    def __init__(self, inc):
        self.increment = inc

    def is11(self):
        for t in range(len(self.increment)):
            if self.increment[t] != 1:
                return False
        return True

    def __str__(self):
        temp = "["
        for t in range(len(self.increment)):
            if t > 0:
                temp += ", "
            temp += str(self.increment[t])
        temp += "]"

        return temp

    def clone(self):
        return deepcopy(self)

    def to_json(self):
        return {"increment": self.increment}
