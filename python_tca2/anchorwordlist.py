from python_tca2 import similarity_utils
from python_tca2.alignment_utils import print_frame
from python_tca2.anchorwordhit import AnchorWordHit
from python_tca2.anchorwordhits import AnchorWordHits
from python_tca2.anchorwordlistentry import AnchorWordListEntry


class AnchorWordList:
    def __init__(self, model):
        print_frame("__init__")
        self.entries = []
        self.model = model

    def load_from_file(self, from_file):
        print_frame("load_from_file")
        self.entries.clear()
        ok = True
        try:
            with open(from_file, "r") as file:
                for line in file:
                    try:
                        self.entries.append(AnchorWordListEntry(line.strip()))
                    except Exception as e:
                        print("Error in anchor word entry:", str(e))
                        ok = False
                        break
        except IOError:
            pass

        if not ok:
            print("Error occurred. Clear list again")
            self.entries.clear()

    def get_anchor_word_hits(self, words, t, element_number):
        print_frame("get_anchor_word_hits")
        ret = AnchorWordHits()
        anchor_word_entry_count = 0
        for entry in self.entries:
            synonyms = entry.language[t]
            for anchor_phrase in synonyms:
                for w in range(len(words) - len(anchor_phrase) + 1):
                    success = True
                    matching_phrase = []  # the actual phrase occurring in the text
                    for w2 in range(len(anchor_phrase)):
                        word = words[w + w2]
                        anchor_word = anchor_phrase[w2]
                        if similarity_utils.anchor_match(anchor_word, word):
                            if w2 > 0:
                                matching_phrase.append(" ")
                            matching_phrase.append(word)
                        else:
                            success = False
                            break
                    if success:
                        hit = AnchorWordHit(
                            anchor_word_entry_count,
                            element_number,
                            w,
                            " ".join(matching_phrase),
                        )
                        ret.add(hit)
            anchor_word_entry_count += 1
        return ret

    def get_proper_names(self, words):
        print_frame("get_proper_names")
        ret = []
        for word in words:
            if len(word) > 0:
                if word[0].isupper():
                    ret.append(word)
        return ret

    def get_scoring_characters(self, text):
        print_frame("get_scoring_characters")
        scoring_characters = self.model.scoring_characters
        ret = ""
        for i in range(len(text)):
            if text[i] in scoring_characters:
                ret += text[i]
        return ret
