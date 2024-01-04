from python_tca2 import constants
from python_tca2.anchorwordhits import AnchorWordHits
from python_tca2.anchorwordlist import AnchorWordList


class ElementInfo:
    def __init__(self, anchor_word_list: AnchorWordList, text, t, element_number):
        # print_frame(text)
        self.length = 0
        self.num_words = 0
        self.words = []
        self.anchor_word_hits = AnchorWordHits()
        self.proper_names = []
        self.scoring_characters = ""

        self.element_number = element_number
        self.length = len(text)
        special_characters = constants.DEFAULT_SPECIAL_CHARACTERS
        special_characters_class = "[\\s"
        for char in special_characters:
            special_characters_class += "\\" + char
        special_characters_class += "]"
        special_characters_pattern = (
            special_characters_class + "*\\s" + special_characters_class + "*"
        )
        temp_words = (" " + text + " ").split(special_characters_pattern)
        self.num_words = len(temp_words) - 1
        self.words = temp_words[1:]
        temp_words = None
        self.anchor_word_hits = anchor_word_list.get_anchor_word_hits(
            self.words, t, element_number
        )
        self.proper_names = anchor_word_list.get_proper_names(self.words)
        self.scoring_characters = anchor_word_list.get_scoring_characters(text)

    def __str__(self):
        # print_frame()
        ret = []
        ret.append("length: " + str(self.length) + ",\n")
        ret.append("numWords: " + str(self.num_words) + ",\n")
        ret.append("words: [\n" + ",\n".join(self.words) + "],\n")
        ret.append(str(self.anchor_word_hits))
        ret.append(",\n")
        ret.append("scoring characters: " + self.scoring_characters + "\n")
        ret.append("proper names: [\n")
        ret.append(",\n".join(self.proper_names))
        ret.append("],\n")

        return "".join(ret)
