import json
from collections import defaultdict

from python_tca2 import (
    constants,
    match,
    similarity_utils,
)
from python_tca2.aelement import AlignmentElement
from python_tca2.alignment_utils import count_words
from python_tca2.anchorwordhit import AnchorWordHit
from python_tca2.anchorwordlist import AnchorWordList
from python_tca2.clusters import Clusters
from python_tca2.elementinfo import ElementInfo
from python_tca2.elementsinfo import ElementsInfo
from python_tca2.exceptions import EndOfAllTextsExceptionError, EndOfTextExceptionError
from python_tca2.pathstep import PathStep
from python_tca2.ref import Ref


# TODO: If ElementInfo and AElement are merged, then as a first step,
# info becomes indexes into e.g. AlignmentModel.elements or whatever
class ElementInfoToBeCompared:
    def __init__(self) -> None:
        self.common_clusters = Clusters()
        self.score = constants.ELEMENTINFO_SCORE_NOT_CALCULATED
        self.info: defaultdict[int, list[ElementInfo]] = defaultdict(list)

    def build_elementstobecompared(  # noqa: PLR0913
        self,
        position: list[int],
        step: PathStep,
        nodes: dict[int, list[AlignmentElement]],
        anchor_word_list: AnchorWordList,
        elements_info: list[ElementsInfo],
    ) -> None:
        text_end_count = 0
        for text_number in nodes.keys():
            for element_index in range(
                position[text_number] + 1,
                position[text_number] + step.increment[text_number] + 1,
            ):
                try:
                    self.info[text_number].append(
                        elements_info[text_number].get_element_info(
                            nodes, anchor_word_list, element_index, text_number
                        )
                    )
                except EndOfTextExceptionError:
                    text_end_count += 1
                    break

        if text_end_count >= constants.NUM_FILES:
            raise EndOfAllTextsExceptionError()

        if text_end_count > 0:
            raise EndOfTextExceptionError()

    def to_json(self):
        return {
            "score": self.get_score(),
            "common_clusters": self.common_clusters.to_json(),
            "info": [info.to_json() for infos in self.info.values() for info in infos],
        }

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def empty(self) -> bool:
        """Both branches of self.info must have elements to be non-empty."""
        return len(self.info) < constants.NUM_FILES

    def get_score(self) -> float:
        if self.score == constants.ELEMENTINFO_SCORE_NOT_CALCULATED:
            self.score = self.calculate_score()

        return self.score

    def has_bad_similarity_score(self) -> float:
        length = [0, 0]
        element_count = [0, 0]

        for text_number in range(constants.NUM_FILES):
            length[text_number] = sum(info.length for info in self.info[text_number])
            element_count[text_number] = len(self.info[text_number])

        return similarity_utils.bad_length_correlation(
            length[0],
            length[1],
            element_count[0],
            element_count[1],
            constants.DEFAULT_LENGTH_RATIO,
        )

    def calculate_clusters_score(self) -> float:
        self.find_anchor_word_matches()
        for text_number1 in range(constants.NUM_FILES):
            for text_number2 in range(text_number1 + 1, constants.NUM_FILES):
                self.find_number_matches(text_number1, text_number2)
                self.find_propername_matches(text_number1, text_number2)
                self.find_dice_matches(text_number1, text_number2)
                self.find_special_character_matches(text_number1, text_number2)

        return self.common_clusters.get_score(
            constants.DEFAULT_LARGE_CLUSTER_SCORE_PERCENTAGE
        )

    def adjust_for_length_correlation(self, score: float) -> float:
        length = [0, 0]
        element_count = [0, 0]

        for text_number in range(constants.NUM_FILES):
            length[text_number] = sum(info.length for info in self.info[text_number])
            element_count[text_number] = len(self.info[text_number])

        return similarity_utils.adjust_for_length_correlation(
            score,
            length[0],
            length[1],
            element_count[0],
            element_count[1],
            constants.DEFAULT_LENGTH_RATIO,
        )

    def calculate_score(self) -> float:
        if self.empty():
            return 0.0
        if self.has_bad_similarity_score():
            return constants.ELEMENTINFO_SCORE_HOPELESS

        cluster_score = self.calculate_clusters_score()
        score = self.adjust_for_length_correlation(score=cluster_score)

        is11: bool = all(
            len(self.info[text_number]) == 1
            for text_number in range(constants.NUM_FILES)
        )

        if not is11:
            score -= 0.001

        return score

    def variables_for_dice_matches(self, text_number1: int, text_number2: int):
        for info1 in self.info[text_number1]:
            for x, word1 in enumerate(info1.words):
                next_word1 = info1.words[x + 1] if x < len(info1.words) - 1 else ""
                for info2 in self.info[text_number2]:
                    for y, word2 in enumerate(info2.words):
                        yield info1, x, word1, next_word1, info2, y, word2

    def find_dice_matches(self, text_number1: int, text_number2: int):
        for (
            info1,
            x,
            word1,
            next_word1,
            info2,
            y,
            word2,
        ) in self.variables_for_dice_matches(text_number1, text_number2):
            match_type = match.DICE
            weight = constants.DEFAULT_DICEPHRASE_MATCH_WEIGHT

            if (
                len(word1) >= constants.DEFAULT_DICE_MIN_WORD_LENGTH
                and len(word2) >= constants.DEFAULT_DICE_MIN_WORD_LENGTH
                and similarity_utils.dice_match1(
                    word1, word2, constants.DEFAULT_DICE_MIN_COUNTING_SCORE
                )
            ):
                ref1 = Ref(
                    match_type,
                    weight,
                    text_number1,
                    info1.element_number,
                    x,
                    1,
                    word1,
                )
                ref2 = Ref(
                    match_type,
                    weight,
                    text_number2,
                    info2.element_number,
                    y,
                    1,
                    word2,
                )
                self.common_clusters.add(ref1, ref2)

            if (
                next_word1 != ""
                and all(
                    len(word) >= constants.DEFAULT_DICE_MIN_WORD_LENGTH
                    for word in [word2, next_word1, word1]
                )
                and similarity_utils.dice_match2(
                    word1,
                    next_word1,
                    word2,
                    "2-1",
                    constants.DEFAULT_DICE_MIN_COUNTING_SCORE,
                )
            ):
                show_phrase = word1 + " " + next_word1
                ref1 = Ref(
                    match_type,
                    weight,
                    text_number1,
                    info1.element_number,
                    x,
                    2,
                    show_phrase,
                )
                ref2 = Ref(
                    match_type,
                    weight,
                    text_number2,
                    info2.element_number,
                    y,
                    1,
                    word2,
                )
                self.common_clusters.add(ref1, ref2)

            next_word2 = info2.words[y + 1] if y < len(info2.words) - 1 else ""
            if (
                next_word2 != ""
                and all(
                    len(word) >= constants.DEFAULT_DICE_MIN_WORD_LENGTH
                    for word in [word1, next_word2, word2]
                )
                and similarity_utils.dice_match2(
                    word1,
                    word2,
                    next_word2,
                    "1-2",
                    constants.DEFAULT_DICE_MIN_COUNTING_SCORE,
                )
            ):
                show_phrase2 = word2 + " " + next_word2
                ref1 = Ref(
                    match_type,
                    weight,
                    text_number1,
                    info1.element_number,
                    x,
                    1,
                    word1,
                )
                ref2 = Ref(
                    match_type,
                    weight,
                    text_number2,
                    info2.element_number,
                    y,
                    2,
                    show_phrase2,
                )

                self.common_clusters.add(ref1, ref2)

    def find_anchor_word_matches(self):
        hits = [
            sorted(lang_hits, key=lambda hit: (hit.index, hit.word))
            for lang_hits in self.find_hits()
        ]
        current = [0] * constants.NUM_FILES
        done = False
        while not done:
            smallest = float("inf")
            smallest_count = 0
            for text_number in range(constants.NUM_FILES):
                if current[text_number] < len(hits[text_number]):
                    hit = hits[text_number][current[text_number]]
                    if hit.index < smallest:
                        smallest = hit.index
                        smallest_count = 1
                    elif hit.index == smallest:
                        smallest_count += 1

            present_in_all_texts = smallest_count == constants.NUM_FILES

            if smallest == float("inf"):
                break

            anchor_word_clusters = Clusters()
            for text_number in range(constants.NUM_FILES):
                if current[text_number] < len(hits[text_number]):
                    current[text_number] += self.make_anchor_word_clusters(
                        hits,
                        current_position=current[text_number],
                        smallest=smallest,
                        present_in_all_texts=present_in_all_texts,
                        anchor_word_clusters=anchor_word_clusters,
                        text_number=text_number,
                    )

            if anchor_word_clusters.clusters:
                self.common_clusters.add_clusters(anchor_word_clusters)

    @staticmethod
    def make_anchor_word_clusters(  # noqa: PLR0913
        hits: list[list[AnchorWordHit]],
        current_position: int,
        smallest: int,
        present_in_all_texts: bool,
        anchor_word_clusters: Clusters,
        text_number: int,
    ):
        hit_counts = 0  # count of hits
        while True:
            if current_position >= len(hits[text_number]):  # if there are no more hits
                return hit_counts  # return the count

            hit = hits[text_number][current_position]  # get the hit
            index = hit.index  # get the index
            if index != smallest:  # if the index is not the smallest
                return hit_counts  # return the count

            if present_in_all_texts:  # if the smallest index is present in all texts
                anchor_word_clusters.add_ref(
                    Ref(
                        match_type=index,
                        weight=(
                            constants.DEFAULT_ANCHORPHRASE_MATCH_WEIGHT
                            if count_words(hit.word) > 1
                            else constants.DEFAULT_ANCHOR_WORD_MATCH_WEIGHT
                        ),
                        text_number=text_number,
                        element_number=hit.element_number,
                        pos=hit.pos,
                        length=count_words(hit.word),
                        word=hit.word,
                    )
                )
            hit_counts += 1  # increment the count
            current_position += 1  # increment the index

    def variables_for_propername_matches(self, text_number1: int, text_number2: int):
        for info1 in self.info[text_number1]:
            for x, word1 in enumerate(info1.words):
                if word1:
                    for info2 in self.info[text_number2]:
                        for y, word2 in enumerate(info2.words):
                            if (
                                word2
                                and word1[0].isupper()
                                and word2[0].isupper()
                                and word1 == word2
                            ):
                                yield info1, x, word1, info2, y, word2

    def find_propername_matches(self, text_number1, text_number2):
        for info1, x, word1, info2, y, word2 in self.variables_for_propername_matches(
            text_number1, text_number2
        ):
            match_type = match.PROPER
            weight = constants.DEFAULT_PROPERNAME_MATCH_WEIGHT
            ref1 = Ref(
                match_type,
                weight,
                text_number1,
                info1.element_number,
                x,
                1,
                word1,
            )
            ref2 = Ref(
                match_type,
                weight,
                text_number2,
                info2.element_number,
                y,
                1,
                word2,
            )
            self.common_clusters.add(ref1=ref1, ref2=ref2)

    def variables_for_number_matches(self, text_number1: int, text_number2: int):
        for info1 in self.info[text_number1]:
            for x, word1 in enumerate(info1.words):
                for info2 in self.info[text_number2]:
                    for y, word2 in enumerate(info2.words):
                        yield info1, x, word1, info2, y, word2

    def find_number_matches(self, text_number1, text_number2):
        for info1, x, word1, info2, y, word2 in self.variables_for_number_matches(
            text_number1, text_number2
        ):
            try:
                num1 = float(word1)
                num2 = float(word2)
                if num1 == num2:
                    # same number
                    # add to cluster list
                    match_type = match.NUMBER
                    weight = constants.DEFAULT_NUMBER_MATCH_WEIGHT
                    ref1 = Ref(
                        match_type,
                        weight,
                        text_number1,
                        info1.element_number,
                        x,
                        1,
                        word1,
                    )
                    ref2 = Ref(
                        match_type,
                        weight,
                        text_number2,
                        info2.element_number,
                        y,
                        1,
                        word2,
                    )
                    self.common_clusters.add(ref1=ref1, ref2=ref2)
            except ValueError:
                pass

    def variables_for_special_character_matches(
        self, text_number1: int, text_number2: int
    ):
        for info1 in self.info[text_number1]:
            for info2 in self.info[text_number2]:
                for char1 in info1.scoring_characters:
                    for char2 in info2.scoring_characters:
                        if char1 == char2:
                            yield info1, info2, char1, char2

    def find_special_character_matches(self, text_number1, text_number2):
        for info1, info2, char1, char2 in self.variables_for_special_character_matches(
            text_number1, text_number2
        ):
            match_type = match.SCORING_CHARACTERS
            weight = constants.DEFAULT_SCORING_CHARACTER_MATCH_WEIGHT
            ref1 = Ref(
                match_type,
                weight,
                text_number1,
                info1.element_number,
                0,
                1,
                char1,
            )
            ref2 = Ref(
                match_type,
                weight,
                text_number2,
                info2.element_number,
                0,
                1,
                char2,
            )
            self.common_clusters.add(ref1=ref1, ref2=ref2)

    def find_hits(self) -> list[list[AnchorWordHit]]:
        return [
            [hit for info in info_list for hit in info.anchor_word_hits.hits]
            for info_list in self.info.values()
        ]
