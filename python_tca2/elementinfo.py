from python_tca2 import constants
from python_tca2.anchorwordhits import AnchorWordHits
from python_tca2.anchorwordlist import AnchorWordList


def remove_special_characters(word):
    for special_char in constants.DEFAULT_SPECIAL_CHARACTERS:
        if word.startswith(special_char):
            word = word[1:]
        if word.endswith(special_char):
            word = word[:-1]

    return word


class ElementInfo:
    def __init__(self, anchor_word_list: AnchorWordList, text, t, element_number):
        self.length = 0
        self.num_words = 0
        self.words = []
        self.anchor_word_hits = AnchorWordHits()
        self.proper_names = []
        self.scoring_characters = ""

        self.element_number = element_number
        self.length = len(text)
        temp_words = [remove_special_characters(word) for word in text.split()]
        print(f"tempWords: {len(temp_words)} {temp_words}")
        self.num_words = len(temp_words)
        self.words = temp_words
        temp_words = None
        self.anchor_word_hits = anchor_word_list.get_anchor_word_hits(
            self.words, t, element_number
        )
        self.proper_names = anchor_word_list.get_proper_names(self.words)
        self.scoring_characters = anchor_word_list.get_scoring_characters(text)

    def __str__(self) -> str:
        # print_frame()
        ret = []
        ret.append("length: " + str(self.length) + ",\n")
        ret.append("numWords: " + str(self.num_words) + ",\n")
        ret.append("words: [\n" + ",\n".join(self.words) + "],\n")
        ret.append(str(self.anchor_word_hits))
        ret.append(",\n")
        ret.append("scoringCharacters: " + self.scoring_characters + ",\n")
        ret.append("properNames: [\n")
        ret.append(",\n".join(self.proper_names))
        ret.append("],\n")

        return "".join(ret)
