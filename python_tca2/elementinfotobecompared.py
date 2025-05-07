import json
from collections import Counter
from itertools import product
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
        element_counts = [
            len(alignment_elements)
            for alignment_elements in self.aligned_sentence_elements
        ]

        # if the number of elements in both branches is equal, we don't need to check
        # for bad length correlation
        if element_counts[0] == element_counts[1]:
            return False

        lengths = [
            sum(alignment_element.length for alignment_element in alignment_elements)
            for alignment_elements in self.aligned_sentence_elements
        ]

        return similarity_utils.bad_length_correlation(
            lengths,
            constants.DEFAULT_LENGTH_RATIO,
        )

    def calculate_clusters_score(self) -> float:
        common_clusters = Clusters()
        for anchor_word_clusters in self.make_anchor_word_clusters():
            common_clusters.add_clusters(anchor_word_clusters)

        for score_function in [
            self.find_number_matches,
            self.find_propername_matches,
            self.find_dice_matches,
            self.find_special_character_matches,
        ]:
            for ref1, ref2 in score_function():
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

    def find_dice_matches(self) -> Iterator[tuple[Ref, Ref]]:
        half_refs = [
            [
                (alignment_element, position)
                for alignment_element in alignment_elements
                for position, _ in enumerate(alignment_element.words)
            ]
            for alignment_elements in self.aligned_sentence_elements
        ]

        for (info1, x), (info2, y) in product(*half_refs):
            if (
                len(info1.words[x]) >= constants.DEFAULT_DICE_MIN_WORD_LENGTH
                and len(info2.words[y]) >= constants.DEFAULT_DICE_MIN_WORD_LENGTH
            ):
                if similarity_utils.dice_match_word_pair(
                    info1.words[x],
                    info2.words[y],
                    constants.DEFAULT_DICE_MIN_COUNTING_SCORE,
                ):
                    yield Ref(
                        match_type=match.DICE,
                        weight=constants.DEFAULT_DICEPHRASE_MATCH_WEIGHT,
                        text_number=info1.text_number,
                        element_number=info1.element_number,
                        pos=x,
                        length=1,
                        word=info1.words[x],
                    ), Ref(
                        match_type=match.DICE,
                        weight=constants.DEFAULT_DICEPHRASE_MATCH_WEIGHT,
                        text_number=info2.text_number,
                        element_number=info2.element_number,
                        pos=y,
                        length=1,
                        word=info2.words[y],
                    )
                next_word1 = info1.words[x + 1] if x < len(info1.words) - 1 else ""
                if len(
                    next_word1
                ) >= constants.DEFAULT_DICE_MIN_WORD_LENGTH and similarity_utils.dice_match_word_with_phrase(
                    phrase=(info1.words[x], next_word1),
                    word=info2.words[y],
                ):
                    yield Ref(
                        match_type=match.DICE,
                        weight=constants.DEFAULT_DICEPHRASE_MATCH_WEIGHT,
                        text_number=info1.text_number,
                        element_number=info1.element_number,
                        pos=x,
                        length=2,
                        word=" ".join(info1.words[x : x + 2]),
                    ), Ref(
                        match_type=match.DICE,
                        weight=constants.DEFAULT_DICEPHRASE_MATCH_WEIGHT,
                        text_number=info2.text_number,
                        element_number=info2.element_number,
                        pos=y,
                        length=1,
                        word=info2.words[y],
                    )

                next_word2 = info2.words[y + 1] if y < len(info2.words) - 1 else ""
                if len(
                    next_word2
                ) >= constants.DEFAULT_DICE_MIN_WORD_LENGTH and similarity_utils.dice_match_word_with_phrase(
                    word=info1.words[x],
                    phrase=(info2.words[y], next_word2),
                ):
                    yield Ref(
                        match_type=match.DICE,
                        weight=constants.DEFAULT_DICEPHRASE_MATCH_WEIGHT,
                        text_number=info1.text_number,
                        element_number=info1.element_number,
                        pos=x,
                        length=1,
                        word=info1.words[x],
                    ), Ref(
                        match_type=match.DICE,
                        weight=constants.DEFAULT_DICEPHRASE_MATCH_WEIGHT,
                        text_number=info2.text_number,
                        element_number=info2.element_number,
                        pos=y,
                        length=2,
                        word=" ".join(info2.words[y : y + 2]),
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

    def find_propername_matches(self) -> Iterator[tuple[Ref, Ref]]:
        pairs = [
            [
                Ref(
                    match_type=match.PROPER,
                    weight=constants.DEFAULT_PROPERNAME_MATCH_WEIGHT,
                    text_number=alignment_element.text_number,
                    element_number=alignment_element.element_number,
                    pos=position,
                    length=1,
                    word=word,
                )
                for alignment_element in alignment_elements
                for position, word in enumerate(alignment_element.words)
            ]
            for alignment_elements in self.aligned_sentence_elements
        ]

        for ref1, ref2 in product(*pairs):
            if (
                ref2.word
                and ref1.word[0].isupper()
                and ref2.word[0].isupper()
                and ref1.word == ref2.word
            ):
                yield ref1, ref2

    def are_words_numbers_and_equal(self, word1: str, word2: str) -> bool:
        """Check if both words are numbers."""
        try:
            return float(word1) == float(word2)
        except ValueError:
            return False

    def find_number_matches(self) -> Iterator[tuple[Ref, Ref]]:
        pairs = [
            [
                Ref(
                    match_type=match.NUMBER,
                    weight=constants.DEFAULT_NUMBER_MATCH_WEIGHT,
                    text_number=alignment_element.text_number,
                    element_number=alignment_element.element_number,
                    pos=position,
                    length=1,
                    word=word,
                )
                for alignment_element in alignment_elements
                for position, word in enumerate(alignment_element.words)
            ]
            for alignment_elements in self.aligned_sentence_elements
        ]

        for ref1, ref2 in product(*pairs):
            if self.are_words_numbers_and_equal(ref1.word, ref2.word):
                yield ref1, ref2

    def find_special_character_matches(self) -> Iterator[tuple[Ref, Ref]]:
        pairs = [
            [
                Ref(
                    match_type=match.SCORING_CHARACTERS,
                    weight=constants.DEFAULT_SCORING_CHARACTER_MATCH_WEIGHT,
                    text_number=alignment_element.text_number,
                    element_number=alignment_element.element_number,
                    pos=0,
                    length=1,
                    word=char,
                )
                for alignment_element in alignment_elements
                for char in alignment_element.scoring_characters
            ]
            for alignment_elements in self.aligned_sentence_elements
        ]

        for ref1, ref2 in product(*pairs):
            if ref1.word == ref2.word:
                yield ref1, ref2

    def find_hits(self) -> list[list[AnchorWordHit]]:
        return [
            [
                hit
                for alignment_element in alignment_elements
                for hit in alignment_element.anchor_word_hits.hits
            ]
            for alignment_elements in self.aligned_sentence_elements
        ]
