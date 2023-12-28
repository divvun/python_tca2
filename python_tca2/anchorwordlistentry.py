import re

from python_tca2 import alignment


class AnchorWordListEntry:
    def __init__(self, anchor_word_list_entry_text):
        self.language = [
            [] for _ in range(alignment.NUM_FILES)
        ]  # ¤¤¤ should probably be 2

        if len(anchor_word_list_entry_text) > 0:
            data = anchor_word_list_entry_text.split(
                "/"
            )  # split entry into array of data for each text/language

            if len(data) < alignment.NUM_FILES:
                raise Exception("No slash: " + anchor_word_list_entry_text)  # §§§
            elif len(data) > alignment.NUM_FILES:
                raise Exception(
                    "Too many slashes: " + anchor_word_list_entry_text
                )  # §§§

            for t in range(alignment.NUM_FILES):
                self.language[t] = []
                syns = data[t].split(
                    ","
                )  # split data for one language into array of "synonyms". each synonym can be a phrase
                for ph in range(len(syns)):
                    words = syns[ph].split(
                        " "
                    )  # split phrase into array of words. in practice most phrases will contain just one word
                    phrase = []  # list to contain one phrase, with one word per element
                    for w in range(len(words)):
                        word = words[w].strip()
                        if word != "":
                            phrase.append(self.makeCompiledPattern(word))
                    if len(phrase) > 0:
                        self.language[t].append(phrase)

    def make_compiled_pattern(self, anchor_word):
        # make a proper regular expression from the anchor word
        pattern = "^" + anchor_word.replace("*", ".*") + "$"
        return re.compile(pattern, re.IGNORECASE | re.UNICODE)
