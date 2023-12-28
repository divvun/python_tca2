class Ref:
    def __init__(self, match_type, weight, t, element_number, pos, length, word):
        self.match_type = match_type
        self.weight = weight
        self.t = t
        self.element_number = element_number
        self.pos = pos
        self.length = length
        self.word = word

    def matches(self, other_ref):
        if (
            (self.t == other_ref.t)
            and (self.element_number == other_ref.element_number)
            and (self.pos <= other_ref.pos + other_ref.length)
            and (other_ref.pos <= self.pos + self.length)
        ):
            return True
        elif other_ref.match_type >= 0:
            if self.match_type == other_ref.match_type:
                return True
        return False

    def exactly_matches(self, other_ref):
        return (
            (self.match_type == other_ref.match_type)
            and (self.t == other_ref.t)
            and (self.element_number == other_ref.element_number)
            and (self.pos == other_ref.pos)
            and (self.length == other_ref.length)
        )

    def get_word(self):
        return self.word

    def get_t(self):
        return self.t

    def get_match_type(self):
        return self.match_type

    def type_anchor_word(self):
        return self.match_type >= 0

    def get_pos(self):
        return self.pos
