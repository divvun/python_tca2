from python_tca2.alignment_utils import print_frame
from python_tca2.anchorwordhit import AnchorWordHit


class AnchorWordHitComparator:
    def compare(self, o1: AnchorWordHit, o2: AnchorWordHit) -> int:
        print_frame("compare")
        if not isinstance(o1, AnchorWordHit):
            raise TypeError()
        if not isinstance(o2, AnchorWordHit):
            raise TypeError()

        index1 = o1.index
        index2 = o2.index

        if index1 < index2:
            return -1
        elif index1 > index2:
            return 1
        else:
            word1 = o1.word
            word2 = o2.word

            return word1.compare(word2)
