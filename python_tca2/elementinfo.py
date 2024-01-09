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


def get_scoring_characters(text: str) -> str:
    scoring_characters = constants.DEFAULT_SCORING_CHARACTERS
    ret = ""
    for i in range(len(text)):
        if text[i] in scoring_characters:
            ret += text[i]
    return ret


def get_upper_case_words(words):
    return [word for word in words if len(word) > 0 and word[0].isupper()]


class ElementInfo:
    def __init__(
        self, anchor_word_list: AnchorWordList, text: str, t: int, element_number: int
    ):
        self.element_number = element_number
        self.length = len(text)
        self.words = [remove_special_characters(word) for word in text.split()]
        self.num_words = len(self.words)
        self.anchor_word_hits: AnchorWordHits = anchor_word_list.get_anchor_word_hits(
            self.words, t, element_number
        )
        self.upper_case_words = get_upper_case_words(self.words)
        self.scoring_characters = get_scoring_characters(text)

    def __str__(self) -> str:
        ret = []
        ret.append("length: " + str(self.length) + ",\n")
        ret.append("numWords: " + str(self.num_words) + ",\n")
        ret.append("words: " + ",\n".join(self.words) + ",\n")
        ret.append(str(self.anchor_word_hits))
        ret.append(",\n")
        ret.append("scoringCharacters: " + self.scoring_characters + ",\n")
        ret.append("properNames: ")
        ret.append(",\n".join(self.upper_case_words))

        return "".join(ret)
