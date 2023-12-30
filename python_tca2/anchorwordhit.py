from python_tca2.alignment_utils import print_frame


class AnchorWordHit:
    def __init__(self, index, element_number, pos, word):
        print_frame()
        self.index = index
        self.element_number = element_number
        self.pos = pos
        self.word = word

    def get_index(self):
        print_frame()
        return self.index

    def get_word(self):
        print_frame()
        return self.word

    def get_pos(self):
        print_frame()
        return self.pos

    def get_element_number(self):
        print_frame()
        return self.elementNumber

    def __str__(self):
        print_frame()
        return (
            "(index="
            + str(self.index)
            + ";pos="
            + str(self.pos)
            + ";word="
            + self.word
            + ")"
        )
