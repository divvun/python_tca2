from python_tca2.anchorwordhits import AnchorWordHits


class ElementInfo:
    def __init__(self, model, text, t, element_number):
        self.length = 0
        self.num_words = 0
        self.words = []
        self.anchor_wordHits = AnchorWordHits()
        self.proper_names = []
        self.scoring_characters = ""

        self.element_number = element_number
        self.length = len(text)
        special_characters = model.getSpecial_characters()
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
        self.anchor_wordHits = model.anchor_wordList.getAnchor_wordHits(
            self.words, t, element_number
        )
        self.proper_names = model.anchor_wordList.get_proper_names(self.words)
        self.scoring_characters = model.anchor_wordList.getScoring_characters(text)

    def __str__(self):
        ret = []
        ret.append("# chars = " + str(self.length))
        ret.append("; ")
        ret.append("# words = " + str(self.num_words))
        ret.append("; ")
        ret.append("words = {" + ", ".join(self.words) + "}")
        ret.append("; ")
        ret.append("anchor word hits = " + str(self.anchor_wordHits))
        ret.append("; ")
        ret.append("proper names = " + str(self.proper_names))
        return "".join(ret)
