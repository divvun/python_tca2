import re

from python_tca2 import constants
from python_tca2.alignment_utils import print_frame


class AnchorWordListEntry:
    def __init__(self, anchor_word_list_entry_text):
        print_frame()
        self.language = [
            [] for _ in range(constants.NUM_FILES)
        ]  # ¤¤¤ should probably be 2

        if len(anchor_word_list_entry_text) > 0:
            data = anchor_word_list_entry_text.split(
                "/"
            )  # split entry into array of data for each text/language

            if len(data) < constants.NUM_FILES:
                raise Exception("No slash: " + anchor_word_list_entry_text)  # §§§
            elif len(data) > constants.NUM_FILES:
                raise Exception(
                    "Too many slashes: " + anchor_word_list_entry_text
                )  # §§§

            for t in range(constants.NUM_FILES):
                self.language[t] = []
                syns = data[t].split(
                    ","
                )  
                for ph in range(len(syns)):
                    words = syns[ph].split(
                        " "
                    ) 
                    phrase = []  # list to contain one phrase, with one word per element
                    for w in range(len(words)):
                        word = words[w].strip()
                        if word != "":
                            phrase.append(self.make_compiled_pattern(word))
                    if len(phrase) > 0:
                        self.language[t].append(phrase)

    def make_compiled_pattern(self, anchor_word):
        print_frame()
        # make a proper regular expression from the anchor word
        pattern = "^" + anchor_word.replace("*", ".*") + "$"
        return re.compile(pattern, re.IGNORECASE | re.UNICODE)
