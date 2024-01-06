class Ref:
    def __init__(self, match_type, weight, t, element_number, pos, length, word):
        # print_frame()
        self.match_type = match_type
        self.weight = weight
        self.t = t
        self.element_number = element_number
        self.pos = pos
        self.length = length
        self.word = word

    def __str__(self) -> str:
        return (
            f"matchType: {self.match_type},\n"
            f"weight: {self.weight},\n"
            f"t: {self.t},\n"
            f"elementNumber: {self.element_number},\n"
            f"pos: {self.pos},\n"
            f"len: {self.length},\n"
            f"word: {self.word}\n"
        )

    def matches(self, other_ref):
        # print_frame()
        if (
            (self.t == other_ref.t)
            and (self.element_number == other_ref.element_number)
            and (self.pos <= other_ref.pos + other_ref.length - 1)
            and (other_ref.pos <= self.pos + self.length - 1)
        ):
            return True
        elif other_ref.match_type >= 0:
            if self.match_type == other_ref.match_type:
                return True
        return False

    def is_in_text(self, t):
        return self.t == t

    def exactly_matches(self, other_ref):
        # print_frame()
        return (
            (self.match_type == other_ref.match_type)
            and (self.t == other_ref.t)
            and (self.element_number == other_ref.element_number)
            and (self.pos == other_ref.pos)
            and (self.length == other_ref.length)
        )

    def type_anchor_word(self):
        # print_frame()
        return self.match_type >= 0
