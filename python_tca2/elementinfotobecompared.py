from python_tca2 import (
    alignment,
    alignment_utils,
    alignmentmodel,
    match,
    similarity_utils,
)
from python_tca2.clusters import Clusters
from python_tca2.ref import Ref


class ElementInfoToBeCompared:
    INDENT = "  "
    info = [[] for _ in range(alignment.NUM_FILES)]
    common_clusters = Clusters()
    score = alignmentmodel.ELEMENTINFO_SCORE_NOT_CALCULATED
    ret = []  # 2006-11-20

    def __init__(self, model):
        self.model = model

    def add(self, element_info, t):
        self.info[t].append(element_info)

    def empty(self):
        for t in range(alignment.NUM_FILES):
            if self.info[t].size() == 0:
                return True

        return False

    def get_score(self):
        if self.score == alignmentmodel.ELEMENTINFO_SCORE_NOT_CALCULATED:
            self.score = self.really_get_score()

        return self.score

    def really_get_score(self):
        if self.score == alignmentmodel.ELEMENTINFO_SCORE_NOT_CALCULATED:
            self.score = 0.0
            if not self.empty():
                length = [0] * alignment.NUM_FILES
                element_count = [0] * alignment.NUM_FILES

                for t in range(alignment.NUM_FILES):
                    it = self.info[t].iterator()
                    while it.hasNext():
                        info1 = it.next()
                        length[t] += info1.length
                    element_count[t] = self.info[t].size()

                if similarity_utils.bad_length_correlation(
                    length[0],
                    length[1],
                    element_count[0],
                    element_count[1],
                    self.model.get_length_ratio(),
                ):
                    self.score = alignmentmodel.ELEMENTINFO_SCORE_HOPELESS
                else:
                    self.score = self.really_get_score2()
        return self.score

    def really_get_score2(self):
        self.find_anchor_word_matches()
        for t in range(alignment.NUM_FILES):
            for tt in range(t + 1, alignment.NUM_FILES):
                self.find_number_matches(t, tt)
                self.find_propername_matches(t, tt)
                self.find_dice_matches(t, tt)
                self.find_special_character_matches(t, tt)

        self.score += self.common_clusters.get_score(
            self.model.get_large_cluster_score_percentage()
        )

        length = [0] * alignment.NUM_FILES
        element_count = [0] * alignment.NUM_FILES

        for t in range(alignment.NUM_FILES):
            for info1 in self.info[t]:
                length[t] += info1.length
            element_count[t] = self.info[t].size()

        self.score = similarity_utils.adjust_for_length_correlation(
            self.score,
            length[0],
            length[1],
            element_count[0],
            element_count[1],
            self.model.get_length_ratio(),
        )

        is11 = True
        for t in range(alignment.NUM_FILES):
            if self.info[t].size != 1:
                is11 = False
                break

        if not is11:
            self.score -= 0.001

        return self.score

    def find_dice_matches(self, t, tt):
        for info1 in self.info[t]:
            for x in range(len(info1.words)):
                word1 = info1.words[x]
                next_word1 = info1.words[x + 1] if x < len(info1.words) else ""
                for info2 in self.info[tt]:
                    for y in range(len(info2.words)):
                        match_type = match.DICE
                        weight = self.model.get_dice_match_weight()
                        word2 = info2.words[y]

                        if (
                            len(word1) > self.model.get_dice_min_word_length()
                            and len(word2) > self.model.get_dice_min_word_length()
                            and similarity_utils.dice_match1(
                                word1, word2, self.model.get_dice_min_counting_score()
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
                                len(word) >= self.model.get_dice_min_word_length()
                                for word in [word2, next_word1, word1]
                            ) and similarity_utils.dice_match2(
                                word1,
                                next_word1,
                                word2,
                                "2-1",
                                self.model.get_dice_min_counting_score(),
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
                                len(word) >= self.model.get_dice_min_word_length()
                                for word in [word1, next_word2, word2]
                            ) and similarity_utils.dice_match2(
                                word1,
                                word2,
                                next_word2,
                                "1-2",
                                self.model.get_dice_min_counting_score(),
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
        current = [0] * alignment.NUM_FILES

        done = False
        smallest = float("inf")
        smallest_count = 0
        while not done:
            for t in range(alignment.NUM_FILES):
                if current[t] < hits[t].size():
                    hit = hits[t].get(current[t])
                    if hit.index < smallest:
                        smallest = hit.index
                        smallest_count = 1
                    elif hit.index == smallest:
                        smallest_count += 1

            present_in_all_texts = smallest_count == alignment.NUM_FILES

            if smallest == float("inf"):
                done = True
            else:
                hits = self.find_more_hits(
                    hits, current, smallest, present_in_all_texts
                )

    def find_propername_matches(self, t, tt):
        for info1 in self.info[t]:
            for x in range(len(info1.words)):
                word1 = info1.words[x]
                for info2 in self.info[tt]:
                    for y in range(len(info2.words)):
                        word2 = info2.words[y]
                        if word1[0].isupper() and word2[0].isupper() and word1 == word2:
                            match_type = match.PROPER
                            weight = self.model.get_proper_name_match_weight()
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
        it1 = self.info[t].iterator()
        while it1.hasNext():
            info1 = it1.next()
            for x in range(len(info1.words)):
                word1 = info1.words[x]
                it2 = self.info[tt].iterator()
                while it2.hasNext():
                    info2 = it2.next()
                    for y in range(len(info2.words)):
                        word2 = info2.words[y]
                        num1 = float(word1)
                        num2 = float(word2)
                        if num1 == num2:
                            # same number
                            # add to cluster list
                            match_type = match.NUMBER
                            weight = self.model.get_number_match_weight()  # 2006-04-07
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

    def find_special_character_matches(self, t, tt):
        for info1 in self.info[t]:
            for info2 in self.info[tt]:
                for char1 in info1.scoring_characters:
                    for char2 in info2.scoring_characters:
                        if char1 == char2:
                            match_type = match.SCORING_CHARACTERS
                            weight = self.model.get_scoring_character_match_weight()
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
        for t in range(alignment.NUM_FILES):
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
                        len_ = alignment_utils.count_words(word)
                        match_type = index
                        weight = (
                            self.model.getAnchorPhraseMatchWeight()
                            if len_ > 1
                            else self.model.getAnchorWordMatchWeight()
                        )
                        if present_in_all_texts:
                            anchor_word_clusters.add(
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

        self.commonClusters.add(anchor_word_clusters)
        return hits

    def find_hits(self):
        return [
            [
                hit
                for info_list in self.info
                for info in info_list
                for hit in info.anchorWordHits.hits
            ]
        ]
