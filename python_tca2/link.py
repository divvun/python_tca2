from python_tca2 import alignment


class Link:
    def __init__(self):
        self.alignment_number = -1
        self.element_numbers = [set() for _ in range(alignment.NUM_FILES)]

    def __str__(self):
        str_ = "("
        for t in range(alignment.NUM_FILES):
            if t > 0:
                str_ += ";"
            str_ += "size=" + str(len(self.element_numbers[t]))
            for el in self.element_numbers[t]:
                str_ += ",el=" + str(el)
        str_ += ")"
        str_ += " alignment number " + str(self.alignment_number)
        return str_
