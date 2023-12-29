from python_tca2.ref import Ref


class RefComparator:
    def compare(self, o1, o2):
        if not isinstance(o1, Ref):
            raise TypeError()
        if not isinstance(o2, Ref):
            raise TypeError()

        match_type1 = o1.get_match_type()
        match_type2 = o2.get_match_type()

        if match_type1 < match_type2:
            return -1
        elif match_type1 > match_type2:
            return 1
        else:
            t = o1.get_t()
            tt = o2.get_t()

            if t < tt:
                return -1
            elif t > tt:
                return 1
            else:
                word1 = o1.get_word()
                word2 = o2.get_word()

                return word1.compare(word2)
