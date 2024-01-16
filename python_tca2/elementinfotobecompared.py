import json
from typing import List

from python_tca2 import (
    constants,
    match,
    similarity_utils,
)
from python_tca2.alignment_utils import count_words
from python_tca2.clusters import Clusters
from python_tca2.elementinfo import ElementInfo
from python_tca2.ref import Ref


# TODO: If ElementInfo and AElement are merged, then as a first step,
# info becomes indexes into e.g. AlignmentModel.elements or whatever
class ElementInfoToBeCompared:
    def __init__(self):
        self.common_clusters = Clusters()
        self.score = constants.ELEMENTINFO_SCORE_NOT_CALCULATED
        self.info: List[List[ElementInfo]] = [[] for _ in range(constants.NUM_FILES)]

    def to_json(self):
        return {
            "score": self.get_score(),
            "common_clusters": self.common_clusters.to_json(),
            "info": [[info.to_json() for info in infos] for infos in self.info],
        }

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def add(self, element_info, t):
        self.info[t].append(element_info)

    def empty(self):
        for t in range(constants.NUM_FILES):
            if len(self.info[t]) == 0:
                return True

        return False

    def get_score(self):
        if self.score == constants.ELEMENTINFO_SCORE_NOT_CALCULATED:
            self.score = self.really_get_score()

        return self.score

    def really_get_score(self):
        if self.score == constants.ELEMENTINFO_SCORE_NOT_CALCULATED:
            self.score = 0.0
            if not self.empty():
                length = [0, 0]
                element_count = [0, 0]

                for t in range(constants.NUM_FILES):
                    for info in self.info[t]:
                        length[t] += info.length
                    element_count[t] = len(self.info[t])

                if similarity_utils.bad_length_correlation(
                    length[0],
                    length[1],
                    element_count[0],
                    element_count[1],
                    constants.DEFAULT_LENGTH_RATIO,
                ):
                    self.score = constants.ELEMENTINFO_SCORE_HOPELESS
                else:
                    self.score = self.really_get_score2()
        return self.score

    def really_get_score2(self):
        self.find_anchor_word_matches()
        for t in range(constants.NUM_FILES):
            for tt in range(t + 1, constants.NUM_FILES):
                self.find_number_matches(t, tt)
                self.find_propername_matches(t, tt)
                self.find_dice_matches(t, tt)
                self.find_special_character_matches(t, tt)

        self.score += self.common_clusters.get_score(
            constants.DEFAULT_LARGE_CLUSTER_SCORE_PERCENTAGE
        )

        length = [0] * constants.NUM_FILES
        element_count = [0] * constants.NUM_FILES

        for t in range(constants.NUM_FILES):
            for info1 in self.info[t]:
                length[t] += info1.length
            element_count[t] = len(self.info[t])

        self.score = similarity_utils.adjust_for_length_correlation(
            self.score,
            length[0],
            length[1],
            element_count[0],
            element_count[1],
            constants.DEFAULT_LENGTH_RATIO,
        )

        is11 = True
        for t in range(constants.NUM_FILES):
            if len(self.info[t]) != 1:
                is11 = False
                break

        if not is11:
            self.score -= 0.001

        return self.score

    def find_dice_matches(self, t: int, tt: int):
        for info1 in self.info[t]:
            for x in range(len(info1.words)):
                word1 = info1.words[x]
                next_word1 = info1.words[x + 1] if x < len(info1.words) - 1 else ""
                for info2 in self.info[tt]:
                    for y in range(len(info2.words)):
                        match_type = match.DICE
                        weight = constants.DEFAULT_DICEPHRASE_MATCH_WEIGHT
                        word2 = info2.words[y]

                        if (
                            len(word1) > constants.DEFAULT_DICE_MIN_WORD_LENGTH
                            and len(word2) > constants.DEFAULT_DICE_MIN_WORD_LENGTH
                            and similarity_utils.dice_match1(
                                word1, word2, constants.DEFAULT_DICE_MIN_COUNTING_SCORE
                            )
                        ):
                            self.common_clusters.add(
                                match_type,
                                weight,
                                t,
                                tt,
                                info1.element_number,
                                info2.element_number,
                                x,
                                y,
                                1,
                                1,
                                word1,
                                word2,
                            )

                        if next_word1 != "":
                            show_phrase = word1 + " " + next_word1
                            if all(
                                len(word) >= constants.DEFAULT_DICE_MIN_WORD_LENGTH
                                for word in [word2, next_word1, word1]
                            ) and similarity_utils.dice_match2(
                                word1,
                                next_word1,
                                word2,
                                "2-1",
                                constants.DEFAULT_DICE_MIN_COUNTING_SCORE,
                            ):
                                self.common_clusters.add(
                                    match_type,
                                    weight,
                                    t,
                                    tt,
                                    info1.element_number,
                                    info2.element_number,
                                    x,
                                    y,
                                    2,
                                    1,
                                    show_phrase,
                                    word2,
                                )

                        next_word2 = (
                            info2.words[y + 1] if y < len(info2.words) - 1 else ""
                        )
                        if next_word2 != "":
                            show_phrase = word2 + " " + next_word2
                            if all(
                                len(word) >= constants.DEFAULT_DICE_MIN_WORD_LENGTH
                                for word in [word1, next_word2, word2]
                            ) and similarity_utils.dice_match2(
                                word1,
                                word2,
                                next_word2,
                                "1-2",
                                constants.DEFAULT_DICE_MIN_COUNTING_SCORE,
                            ):
                                show_phrase2 = word2 + " " + next_word2
                                self.common_clusters.add(
                                    match_type,
                                    weight,
                                    t,
                                    tt,
                                    info1.element_number,
                                    info2.element_number,
                                    x,
                                    y,
                                    1,
                                    2,
                                    word1,
                                    show_phrase2,
                                )

    def find_anchor_word_matches(self):
        hits = self.find_hits()
        # TODO: sort the hits
        current = [0] * constants.NUM_FILES
        previous_hits = hits
        # The loop is a hideous hack to avoid infinite loops
        # TODO: fix the reason for the infinite loop
        for _ in range(10):
            smallest = float("inf")
            smallest_count = 0
            for t in range(constants.NUM_FILES):
                if current[t] < len(hits[t]):
                    hit = hits[t][current[t]]
                    if hit.index < smallest:
                        smallest = hit.index
                        smallest_count = 1
                    elif hit.index == smallest:
                        smallest_count += 1
            present_in_all_texts = smallest_count == constants.NUM_FILES

            if smallest == float("inf"):
                break

            # This if statement is a hideous hack to avoid infinite loops, as well
            # TODO: fix the reason for the infinite loop
            if hits != previous_hits:
                previous_hits = hits
                hits = self.find_more_hits(
                    hits, current, smallest, present_in_all_texts
                )

    def find_propername_matches(self, t, tt):
        for info1 in self.info[t]:
            for x, word1 in enumerate(info1.words):
                if word1:
                    for info2 in self.info[tt]:
                        for y, word2 in enumerate(info2.words):
                            if (
                                word1[0].isupper()
                                and word2[0].isupper()
                                and word1 == word2
                            ):
                                match_type = match.PROPER
                                weight = constants.DEFAULT_PROPERNAME_MATCH_WEIGHT
                                self.common_clusters.add(
                                    match_type,
                                    weight,
                                    t,
                                    tt,
                                    info1.element_number,
                                    info2.element_number,
                                    x,
                                    y,
                                    1,
                                    1,
                                    word1,
                                    word2,
                                )

    def find_number_matches(self, t, tt):
        for info1 in self.info[t]:
            for x in range(len(info1.words)):
                word1 = info1.words[x]
                for info2 in self.info[tt]:
                    for y in range(len(info2.words)):
                        word2 = info2.words[y]
                        try:
                            num1 = float(word1)
                            num2 = float(word2)
                            if num1 == num2:
                                # same number
                                # add to cluster list
                                match_type = match.NUMBER
                                weight = constants.DEFAULT_NUMBER_MATCH_WEIGHT
                                self.common_clusters.add(
                                    match_type,
                                    weight,
                                    t,
                                    tt,
                                    info1.element_number,
                                    info2.element_number,
                                    x,
                                    y,
                                    1,
                                    1,
                                    word1,
                                    word2,
                                )  # 2006-04-07
                        except ValueError:
                            pass

    def find_special_character_matches(self, t, tt):
        for info1 in self.info[t]:
            for info2 in self.info[tt]:
                for char1 in info1.scoring_characters:
                    for char2 in info2.scoring_characters:
                        if char1 == char2:
                            match_type = match.SCORING_CHARACTERS
                            weight = constants.DEFAULT_SCORING_CHARACTER_MATCH_WEIGHT
                            self.common_clusters.add(
                                match_type,
                                weight,
                                t,
                                tt,
                                info1.element_number,
                                info2.element_number,
                                info1.scoring_characters.index(char1),
                                info2.scoring_characters.index(char2),
                                1,
                                1,
                                char1,
                                char2,
                            )

    # manuelt portet
    def find_more_hits(self, hits, current, smallest, present_in_all_texts):
        anchor_word_clusters = Clusters()
        for t in range(constants.NUM_FILES):
            count = 0
            if current[t] < len(hits[t]):
                done2 = False
                while not done2:
                    c = current[t]
                    hit = hits[t][c]
                    index = hit.index
                    if index == smallest:
                        element_number = hit.element_number
                        pos = hit.pos
                        word = hit.word
                        len_ = count_words(word)
                        match_type = index
                        weight = (
                            constants.DEFAULT_ANCHORPHRASE_MATCH_WEIGHT
                            if len_ > 1
                            else constants.DEFAULT_ANCHOR_WORD_MATCH_WEIGHT
                        )
                        if present_in_all_texts:
                            anchor_word_clusters.add_ref(
                                Ref(
                                    match_type,
                                    weight,
                                    t,
                                    element_number,
                                    pos,
                                    len_,
                                    word,
                                )
                            )
                        count += 1
                    else:
                        done2 = True

                    if c + 1 >= len(hits[t]):
                        done2 = True
                    c += 1
                current[t] += count

        if anchor_word_clusters.clusters:
            self.common_clusters.add_clusters(anchor_word_clusters)
        return hits

    def find_hits(self):
        hits = [[] for _ in range(constants.NUM_FILES)]
        for t, info_list in enumerate(self.info):
            for info in info_list:
                for hit in info.anchor_word_hits.hits:
                    hits[t].append(hit)

        return hits
