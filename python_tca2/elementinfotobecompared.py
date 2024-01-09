from python_tca2 import (
    constants,
    match,
    similarity_utils,
)
from python_tca2.alignment_utils import count_words, print_frame
from python_tca2.clusters import Clusters
from python_tca2.ref import Ref


class ElementInfoToBeCompared:
    def __init__(self):
        # print_frame()
        self.common_clusters = Clusters()
        self.score = constants.ELEMENTINFO_SCORE_NOT_CALCULATED
        self.info = [[] for _ in range(constants.NUM_FILES)]

    def __str__(self):
        poff = []
        for t, infos in enumerate(self.info):
            poff.append(f"text[{t}]: ")
            for info in infos:
                poff.append(f"{info},")

        return (
            f"score: {self.get_score()},\n"
            "common_clusters: "
            f"{self.common_clusters},\n"
            f"{'\n'.join(poff)}"
        )

    def add(self, element_info, t):
        print(f"eitbc add: {t} {element_info}")
        self.info[t].append(element_info)

    def empty(self):
        # print_frame()
        for t in range(constants.NUM_FILES):
            if len(self.info[t]) == 0:
                return True

        return False

    def get_score(self):
        # print_frame()
        if self.score == constants.ELEMENTINFO_SCORE_NOT_CALCULATED:
            print("score not calculated")
            self.score = self.really_get_score()
        print("score", self.score)
        return self.score

    def really_get_score(self):
        # print_frame()
        if self.score == constants.ELEMENTINFO_SCORE_NOT_CALCULATED:
            self.score = 0.0
            if not self.empty():
                print("not empty")
                length = [0, 0]
                element_count = [0, 0]

                for t in range(constants.NUM_FILES):
                    print(f"t: {t} {len(self.info[t])}")
                    for info in self.info[t]:
                        print(f"info: {t} {info}")
                        length[t] += info.length
                    element_count[t] = len(self.info[t])

                print("length correlation:", length, element_count)
                if similarity_utils.bad_length_correlation(
                    length[0],
                    length[1],
                    element_count[0],
                    element_count[1],
                    constants.DEFAULT_LENGTH_RATIO,
                ):
                    print("bad length correlation")
                    self.score = constants.ELEMENTINFO_SCORE_HOPELESS
                else:
                    self.score = self.really_get_score2()
        return self.score

    def really_get_score2(self):
        # print_frame()
        self.find_anchor_word_matches()
        for t in range(constants.NUM_FILES):
            for tt in range(t + 1, constants.NUM_FILES):
                print(
                    f"1 t: {t}, tt: {tt}, clusters: "
                    f"{len(self.common_clusters.clusters)}"
                )
                self.find_number_matches(t, tt)
                print(
                    f"2 t: {t}, tt: {tt}, clusters: "
                    f"{len(self.common_clusters.clusters)}"
                )
                self.find_propername_matches(t, tt)
                print(
                    f"3 t: {t}, tt: {tt}, clusters: "
                    f"{len(self.common_clusters.clusters)}"
                )
                self.find_dice_matches(t, tt)
                print(
                    f"4 t: {t}, tt: {tt}, clusters: "
                    f"{len(self.common_clusters.clusters)}"
                )
                self.find_special_character_matches(t, tt)
                print(
                    f"5 t: {t}, tt: {tt}, clusters: "
                    f"{len(self.common_clusters.clusters)}"
                )

        self.score += self.common_clusters.get_score(
            constants.DEFAULT_LARGE_CLUSTER_SCORE_PERCENTAGE
        )
        print("1 g2 score", self.score)

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
        print("2 g2 score", self.score)

        is11 = True
        for t in range(constants.NUM_FILES):
            if len(self.info[t]) != 1:
                is11 = False
                break

        if not is11:
            self.score -= 0.001

        print("3 g2 score", self.score)
        return self.score

    def find_dice_matches(self, t, tt):
        # print_frame()
        for info1 in self.info[t]:
            print(f"info1: {info1}")
            for x in range(len(info1.words)):
                word1 = info1.words[x]
                next_word1 = info1.words[x + 1] if x < len(info1.words) - 1 else ""
                for info2 in self.info[tt]:
                    print(f"info2: {info2}")
                    for y in range(len(info2.words)):
                        match_type = match.DICE
                        weight = constants.DEFAULT_DICEPHRASE_MATCH_WEIGHT
                        word2 = info2.words[y]
                        print("word1: " + word1 + ", word2: " + word2)
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
                            print(f"1 fd {self.common_clusters}")
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
                                print(f"2 fd {self.common_clusters}")

                        next_word2 = (
                            info2.words[y + 1] if y < len(info2.words) - 1 else ""
                        )
                        if next_word2 != "":
                            print("word1: " + word1 + ", next_word2: " + next_word2)
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
                                print(f"3 fd {self.common_clusters}")

    def find_anchor_word_matches(self):
        # print_frame()
        hits = self.find_hits()
        # TODO: sort the hits
        current = [0] * constants.NUM_FILES

        done = False
        smallest = float("inf")
        smallest_count = 0
        while not done:
            for t in range(constants.NUM_FILES):
                if current[t] < len(hits[t]):
                    hit = hits[t].get(current[t])
                    if hit.index < smallest:
                        smallest = hit.index
                        smallest_count = 1
                    elif hit.index == smallest:
                        smallest_count += 1

            present_in_all_texts = smallest_count == constants.NUM_FILES

            if smallest == float("inf"):
                done = True
            else:
                hits = self.find_more_hits(
                    hits, current, smallest, present_in_all_texts
                )

    def find_propername_matches(self, t, tt):
        # print_frame()
        for info1 in self.info[t]:
            for x in range(len(info1.words)):
                word1 = info1.words[x]
                for info2 in self.info[tt]:
                    for y in range(len(info2.words)):
                        word2 = info2.words[y]
                        if word1[0].isupper() and word2[0].isupper() and word1 == word2:
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
        # print_frame()
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
        # print_frame()
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
        print_frame()
        anchor_word_clusters = Clusters()
        for t in range(constants.NUM_FILES):
            count = 0
            if current[t] < hits[t].size():
                done2 = False
                while not done2:
                    c = current[t]
                    hit = hits[t].get(c)
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

                    if c + 1 >= hits[t].size():
                        done2 = True
                    c += 1
                current[t] += count

        self.commonClusters.add_clusters(anchor_word_clusters)
        return hits

    def find_hits(self):
        # print_frame()
        hits = [[] for _ in range(constants.NUM_FILES)]
        for t, info_list in enumerate(self.info):
            for info in info_list:
                for hit in info.anchor_word_hits.hits:
                    hits[t].append(hit)

        return hits
