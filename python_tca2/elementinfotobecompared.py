import json
from collections import Counter
from typing import Iterator

from python_tca2 import (
    constants,
    match,
    similarity_utils,
)
from python_tca2.aligned_sentence_elements import AlignedSentenceElements
from python_tca2.alignment_utils import count_words
from python_tca2.anchorwordhit import AnchorWordHit
from python_tca2.clusters import Clusters
from python_tca2.ref import Ref


class ElementInfoToBeCompared:
    def __init__(
        self,
        aligned_sentence_elements: AlignedSentenceElements,
    ) -> None:
        self.aligned_sentence_elements = aligned_sentence_elements
        self.score: float | None = None

    def to_json(self):
        return {
            "score": self.get_score(),
            "info": [
                alignment_element.to_json()
                for alignment_elements in self.aligned_sentence_elements
                for alignment_element in alignment_elements
            ],
        }

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def empty(self) -> bool:
        """Both branches of self.info must have elements to be non-empty."""
        return not all(self.aligned_sentence_elements)

    def get_score(self) -> float:
        if self.score is None:
            self.score = self.calculate_score()

        return self.score

    def has_bad_similarity_score(self) -> float:
        lengths = [
            sum(alignment_element.length for alignment_element in alignment_elements)
            for alignment_elements in self.aligned_sentence_elements
        ]
        element_counts = [
            len(alignment_elements)
            for alignment_elements in self.aligned_sentence_elements
        ]

        return similarity_utils.bad_length_correlation(
            lengths,
            element_counts,
            constants.DEFAULT_LENGTH_RATIO,
        )

    def calculate_clusters_score(self) -> float:
        common_clusters = Clusters()
        for anchor_word_clusters in self.make_anchor_word_clusters():
            common_clusters.add_clusters(anchor_word_clusters)

        for text_number1 in range(constants.NUM_FILES):
            for text_number2 in range(text_number1 + 1, constants.NUM_FILES):
                for ref1, ref2 in self.find_number_matches(text_number1, text_number2):
                    common_clusters.create_and_add_cluster(ref1=ref1, ref2=ref2)
                for ref1, ref2 in self.find_propername_matches(
                    text_number1, text_number2
                ):
                    common_clusters.create_and_add_cluster(ref1=ref1, ref2=ref2)
                for ref1, ref2 in self.find_dice_matches(text_number1, text_number2):
                    common_clusters.create_and_add_cluster(ref1=ref1, ref2=ref2)
                for ref1, ref2 in self.find_special_character_matches(
                    text_number1, text_number2
                ):
                    common_clusters.create_and_add_cluster(ref1=ref1, ref2=ref2)

        return common_clusters.get_score()

    def adjust_for_length_correlation(self, score: float) -> float:
        lengths = [
            sum(alignment_element.length for alignment_element in alignment_elements)
            for alignment_elements in self.aligned_sentence_elements
        ]
        element_counts = [
            len(alignment_elements)
            for alignment_elements in self.aligned_sentence_elements
        ]

        return similarity_utils.adjust_for_length_correlation(
            score,
            lengths,
            element_counts,
            ratio=constants.DEFAULT_LENGTH_RATIO,
        )

    def is11(self) -> bool:
        """Check if all elements in self.info have a length of 1."""
        return all(
            len(alignment_elements) == 1
            for alignment_elements in self.aligned_sentence_elements
        )

    def calculate_score(self) -> float:
        if self.empty():
            return 0.0

        if self.has_bad_similarity_score():
            return constants.ELEMENTINFO_SCORE_HOPELESS

        cluster_score = self.calculate_clusters_score()
        score = self.adjust_for_length_correlation(score=cluster_score)

        return score if self.is11() else score - 0.001

    def variables_for_dice_matches(self, text_number1: int, text_number2: int):
        for alignment_elements1 in self.aligned_sentence_elements[text_number1]:
            for x, word1 in enumerate(alignment_elements1.words):
                next_word1 = (
                    alignment_elements1.words[x + 1]
                    if x < len(alignment_elements1.words) - 1
                    else ""
                )
                for alignment_elements2 in self.aligned_sentence_elements[text_number2]:
                    for y, word2 in enumerate(alignment_elements2.words):
                        yield alignment_elements1, x, word1, next_word1, alignment_elements2, y, word2

    def find_dice_matches(
        self, text_number1: int, text_number2: int
    ) -> Iterator[tuple[Ref, Ref]]:
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
                yield Ref(
                    match_type,
                    weight,
                    text_number1,
                    info1.element_number,
                    x,
                    1,
                    word1,
                ), Ref(
                    match_type,
                    weight,
                    text_number2,
                    info2.element_number,
                    y,
                    1,
                    word2,
                )

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
                yield Ref(
                    match_type,
                    weight,
                    text_number1,
                    info1.element_number,
                    x,
                    2,
                    show_phrase,
                ), Ref(
                    match_type,
                    weight,
                    text_number2,
                    info2.element_number,
                    y,
                    1,
                    word2,
                )

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
                yield Ref(
                    match_type,
                    weight,
                    text_number1,
                    info1.element_number,
                    x,
                    1,
                    word1,
                ), Ref(
                    match_type,
                    weight,
                    text_number2,
                    info2.element_number,
                    y,
                    2,
                    show_phrase2,
                )

    def get_these_hits(
        self, hits: list[list[AnchorWordHit]], current: list[int]
    ) -> list[AnchorWordHit]:
        return [
            hits[text_number][current[text_number]]
            for text_number in range(constants.NUM_FILES)
            if current[text_number] < len(hits[text_number])
        ]

    def make_anchor_word_clusters(self) -> Iterator[Clusters]:
        hits = [
            sorted(lang_hits, key=lambda hit: (hit.index, hit.word))
            for lang_hits in self.find_hits()
        ]
        current = [0] * constants.NUM_FILES
        while these_hits := self.get_these_hits(hits, current):
            hit_counter = Counter(hit.index for hit in these_hits)
            smallest_hit_index = min(hit_counter.keys())

            anchor_word_clusters = Clusters()
            for ref in self.make_anchor_word_refs(
                hits,
                current=current,
                smallest=smallest_hit_index,
                present_in_all_texts=hit_counter[smallest_hit_index]
                == constants.NUM_FILES,
            ):
                anchor_word_clusters.add_ref(ref)

            if anchor_word_clusters.clusters:
                yield anchor_word_clusters

    @staticmethod
    def get_hit(
        current_position: int,
        smallest: int,
        hits: list[list[AnchorWordHit]],
        text_number: int,
    ) -> AnchorWordHit | None:
        try:
            hit = hits[text_number][current_position]  # get the hit
        except IndexError:
            return None

        return None if hit.index != smallest else hit

    def make_anchor_word_refs(
        self,
        hits: list[list[AnchorWordHit]],
        current: list[int],
        smallest: int,
        present_in_all_texts: bool,
    ) -> Iterator[Ref]:
        for text_number in range(constants.NUM_FILES):
            if current[text_number] < len(hits[text_number]):
                while (
                    hit := self.get_hit(
                        current[text_number], smallest, hits, text_number
                    )
                ) is not None:
                    if (
                        present_in_all_texts
                    ):  # if the smallest index is present in all texts
                        yield Ref(
                            match_type=hit.index,
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

                    current[text_number] += 1  # increment the count

    def variables_for_propername_matches(self, text_number1: int, text_number2: int):
        for alignment_elements1 in self.aligned_sentence_elements[text_number1]:
            for x, word1 in enumerate(alignment_elements1.words):
                if word1:
                    for alignment_elements2 in self.aligned_sentence_elements[
                        text_number2
                    ]:
                        for y, word2 in enumerate(alignment_elements2.words):
                            if (
                                word2
                                and word1[0].isupper()
                                and word2[0].isupper()
                                and word1 == word2
                            ):
                                yield alignment_elements1, x, word1, alignment_elements2, y, word2

    def find_propername_matches(
        self, text_number1, text_number2
    ) -> Iterator[tuple[Ref, Ref]]:
        for info1, x, word1, info2, y, word2 in self.variables_for_propername_matches(
            text_number1, text_number2
        ):
            match_type = match.PROPER
            weight = constants.DEFAULT_PROPERNAME_MATCH_WEIGHT
            yield Ref(
                match_type,
                weight,
                text_number1,
                info1.element_number,
                x,
                1,
                word1,
            ), Ref(
                match_type,
                weight,
                text_number2,
                info2.element_number,
                y,
                1,
                word2,
            )

    def variables_for_number_matches(self, text_number1: int, text_number2: int):
        for alignment_elements1 in self.aligned_sentence_elements[text_number1]:
            for x, word1 in enumerate(alignment_elements1.words):
                for alignment_elements2 in self.aligned_sentence_elements[text_number2]:
                    for y, word2 in enumerate(alignment_elements2.words):
                        yield alignment_elements1, x, word1, alignment_elements2, y, word2

    def find_number_matches(
        self, text_number1, text_number2
    ) -> Iterator[tuple[Ref, Ref]]:
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
                    yield Ref(
                        match_type,
                        weight,
                        text_number1,
                        info1.element_number,
                        x,
                        1,
                        word1,
                    ), Ref(
                        match_type,
                        weight,
                        text_number2,
                        info2.element_number,
                        y,
                        1,
                        word2,
                    )
            except ValueError:
                pass

    def variables_for_special_character_matches(
        self, text_number1: int, text_number2: int
    ):
        for alignment_elements1 in self.aligned_sentence_elements[text_number1]:
            for aligment_elements2 in self.aligned_sentence_elements[text_number2]:
                for char1 in alignment_elements1.scoring_characters:
                    for char2 in aligment_elements2.scoring_characters:
                        if char1 == char2:
                            yield alignment_elements1, aligment_elements2, char1, char2

    def find_special_character_matches(
        self, text_number1, text_number2
    ) -> Iterator[tuple[Ref, Ref]]:
        for info1, info2, char1, char2 in self.variables_for_special_character_matches(
            text_number1, text_number2
        ):
            match_type = match.SCORING_CHARACTERS
            weight = constants.DEFAULT_SCORING_CHARACTER_MATCH_WEIGHT
            yield Ref(
                match_type,
                weight,
                text_number1,
                info1.element_number,
                0,
                1,
                char1,
            ), Ref(
                match_type,
                weight,
                text_number2,
                info2.element_number,
                0,
                1,
                char2,
            )

    def find_hits(self) -> list[list[AnchorWordHit]]:
        return [
            [
                hit
                for alignment_element in alignment_elements
                for hit in alignment_element.anchor_word_hits.hits
            ]
            for alignment_elements in self.aligned_sentence_elements
        ]
