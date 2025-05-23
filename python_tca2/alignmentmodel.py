from functools import cache
from typing import Iterator

from python_tca2 import alignment_suggestion, constants
from python_tca2.aelement import AlignmentElement
from python_tca2.aligned import Aligned
from python_tca2.aligned_sentence_elements import AlignedSentenceElements
from python_tca2.alignment_suggestion import AlignmentSuggestion
from python_tca2.anchorwordlist import AnchorWordList
from python_tca2.elementinfotobecompared import ElementInfoToBeCompared
from python_tca2.path_candidate import PathCandidate
from python_tca2.path_candidates import PathCandidates


class AlignmentModel:
    scoring_characters = constants.DEFAULT_SCORING_CHARACTERS
    max_path_length = constants.MAX_PATH_LENGTH

    def __init__(
        self,
        sentences_tuple: tuple[list[str], list[str]],
        anchor_word_list: AnchorWordList,
    ) -> None:
        self.anchor_word_list = anchor_word_list
        self.parallel_documents = tuple(
            self.load_sentences(
                text_number=text_number,
                sentences=sentences,
            )
            for text_number, sentences in enumerate(sentences_tuple)
        )

    def get_aligned_sentence_elements(
        self, slices: tuple[slice, slice]
    ) -> AlignedSentenceElements:
        """Returns the next AlignmentElement object for the specified text number.

        Args:
            alignment_suggestion: How man elements to move in each text.

        Returns:
            A tuple of AlignmentElement objects for each text.
        """
        return (
            self.parallel_documents[0][slices[0]],
            self.parallel_documents[1][slices[1]],
        )

    def load_sentences(
        self, text_number: int, sentences: list[str]
    ) -> list[AlignmentElement]:
        """Extracts and processes sentences from an XML tree.

        Args:
            tree: An XML tree containing sentence elements.

        Returns:
            A list of AlignmentElement objects, each representing a sentence.
        """
        return [
            AlignmentElement(
                anchor_word_list=self.anchor_word_list,
                text=sentence,
                text_number=text_number,
                element_number=index,
            )
            for index, sentence in enumerate(sentences)
        ]

    def suggest_without_gui(self) -> Aligned:
        """Suggest alignments.

        This method performs text alignment by iteratively processing paths
        and updating alignment and comparison objects. It stops when alignment
        is complete or a predefined run limit is exceeded.

        Returns:
            A tuple containing the aligned object and the comparison object.
        """
        aligned = Aligned([])

        start_position = (0, 0)
        while (
            alignment_suggestion := self.retrieve_alignment_suggestion(
                start_position=start_position
            )
        ) is not None:
            aligned.pickup(
                self.get_aligned_sentence_elements(
                    slices=(
                        slice(
                            start_position[0],
                            start_position[0] + alignment_suggestion[0],
                        ),
                        slice(
                            start_position[1],
                            start_position[1] + alignment_suggestion[1],
                        ),
                    )
                )
            )
            start_position = (
                start_position[0] + alignment_suggestion[0],
                start_position[1] + alignment_suggestion[1],
            )

        return aligned

    def retrieve_alignment_suggestion(
        self,
        start_position: tuple[int, int],
    ) -> AlignmentSuggestion | None:

        path_candidates = self.extend_alignment_paths(start_position=start_position)

        if (
            len(path_candidates.entries) < constants.NUM_FILES
            and not path_candidates.entries[0].alignment_suggestions
        ):
            # When the length of the queue list is less than the number of files
            # and the first path in the queue list has no steps, then aligment
            # is done
            return None

        return self.select_best_alignment_suggestion(path_candidates)

    def select_best_alignment_suggestion(
        self, path_candidates: PathCandidates
    ) -> AlignmentSuggestion | None:
        """Selects the best alignment suggestion based on normalized scores.

        This method evaluates each candidate entry in the provided queue list by
        calculating a normalized score, which is the candidate's score divided
        by the length of its path in sentences.

        It then selects the first step suggestion from the path with the highest
        normalized score.

        Args:
            path_candidates : A collection of candidate entries, where each entry
                            contains a path and an associated score.

        Returns:
            The first step suggestion from the best path, or None if no entries
            are found.
        """
        score_step_list = [
            (
                candidate_entry.normalized_score,
                candidate_entry.alignment_suggestions[0],
            )
            for candidate_entry in path_candidates.entries
        ]

        return max(score_step_list, key=lambda x: x[0])[1] if score_step_list else None

    def extend_alignment_paths(
        self,
        start_position: tuple[int, int],
    ) -> PathCandidates:
        """Lengthens paths in a text pair alignment process.

        This method iteratively extends paths in the alignment model until no
        further extensions are possible or a maximum path length is reached.

        Args:
            start_position: The starting position in the alignment.

        Returns:
            A QueueList containing the final set of extended paths.
        """
        best_path_scores: dict[str, float] = {}
        path_candidates = PathCandidates([PathCandidate(position=start_position)])
        for _ in range(self.max_path_length):
            next_path_candidates = PathCandidates([])
            for path_candidate in path_candidates.entries:
                if not path_candidate.end:
                    for new_path_candidate in self.extend_current_path(
                        path_candidate,
                        best_path_scores=best_path_scores,
                    ):
                        if new_path_candidate is not None:
                            pos = new_path_candidate.position
                            path_candidates.entries = [
                                path_candidate
                                for path_candidate in path_candidates.entries
                                if not path_candidate.has_hit(pos)
                            ]
                            next_path_candidates.entries = [
                                path_candidate
                                for path_candidate in next_path_candidates.entries
                                if not path_candidate.has_hit(pos)
                            ]
                            if new_path_candidate not in next_path_candidates.entries:
                                next_path_candidates.entries.append(new_path_candidate)

            if not next_path_candidates.entries:
                return path_candidates

            path_candidates = next_path_candidates

        return path_candidates

    def extend_current_path(
        self,
        path_candidate: PathCandidate,
        best_path_scores: dict[str, float],
    ) -> Iterator[PathCandidate | None]:
        """Extends the current path in the alignment process.

        This method iterates through a list of steps to attempt extending the
        current path represented by the given queue entry. It handles various
        exceptions to manage the end of texts or blocked paths.

        Args:
            path_candidate: The current queue entry to be extended.
            path_candidates: The list of current queue entries.
            next_path_candidates: The list of queue entries for the next iteration.
            best_path_scores: A dictionary to store the best path scores.
        Yields:
            QueueEntry: A new queue entry representing the extended path or None if
                the path cannot be extended further.
        """
        for step in alignment_suggestion.generate_alignment_suggestions(
            len(self.parallel_documents)
        ):
            yield self.extend_path_with_step(
                old_position=path_candidate.position,
                old_score=path_candidate.score,
                alignment_suggestions=path_candidate.alignment_suggestions + [step],
                best_path_scores=best_path_scores,
            )

    @cache
    def get_step_score(
        self,
        slices: tuple[slice, slice],
    ) -> float:
        """Calculate the score for a given step at a specific position.

        Args:
            position: The current position in the alignment.
            step: The step to evaluate.

        Returns:
            The score for the specified step.
        """
        eitbc = ElementInfoToBeCompared(
            aligned_sentence_elements=self.get_aligned_sentence_elements(
                slices=slices,
            )
        )

        return eitbc.get_score()

    def will_reach_both_ends(self, position: tuple[int, ...]) -> bool:
        """Check if the current position will reach the end of the texts.

        Args:
            position: The current position in the alignment.

        Returns:
            True if the end of the texts are reached, False otherwise.
        """
        return all(
            current_position > len(n)
            for current_position, n in zip(
                position,
                self.parallel_documents,
                strict=True,
            )
        )

    def will_reach_one_end(
        self,
        position: tuple[int, ...],
    ) -> bool:
        """Check if the current position will reach the end of a text.

        Args:
            position: The current position in the alignment.

        Returns:
            True if at least the end of one of the texts is reached, False otherwise.
        """
        return any(
            current_position > len(n)
            for current_position, n in zip(
                position,
                self.parallel_documents,
                strict=True,
            )
        )

    def extend_path_with_step(
        self,
        old_position: tuple[int, int],
        old_score: float,
        alignment_suggestions: list[AlignmentSuggestion],
        best_path_scores: dict[str, float],
    ) -> PathCandidate | None:
        """Extend a path with a new step and update its score.

        Args:
            ret_path_candidate: The current queue entry containing the path and score.
            alignment_suggestion: The new alignement suggestion to add to the path.
            best_path_scores: A dictionary to store the best path scores.

        Returns:
            The updated queue entry if the new score is better, otherwise None.
        """
        current_alignment_step = alignment_suggestions[-1]
        new_position = (
            old_position[0] + current_alignment_step[0],
            old_position[1] + current_alignment_step[1],
        )

        if self.will_reach_both_ends(new_position):
            return PathCandidate(
                position=old_position,
                score=old_score,
                alignment_suggestions=alignment_suggestions[:-1],
                end=True,
            )

        if self.will_reach_one_end(new_position):
            return None

        position_step_score = self.get_step_score(
            slices=(
                slice(old_position[0], new_position[0]),
                slice(old_position[1], new_position[1]),
            )
        )

        if position_step_score == constants.ELEMENTINFO_SCORE_HOPELESS:
            return None

        new_score = old_score + position_step_score

        best_path_score = get_best_path_score(
            new_position, best_path_scores=best_path_scores
        )

        if best_path_score is not None and new_score <= best_path_score:
            return None

        set_best_path_score(
            new_position,
            new_score,
            best_path_scores=best_path_scores,
        )

        return PathCandidate(
            position=new_position,
            score=new_score,
            alignment_suggestions=alignment_suggestions,
        )


def set_best_path_score(
    position: tuple[int, ...], score: float, best_path_scores: dict[str, float]
) -> None:
    """Sets the score for a specific position in the best path scores.

    Args:
        position: A list representing the position in the path.
        score: The score to assign to the specified position.
    """
    best_path_score_key = ",".join(str(pos) for pos in position)
    best_path_scores[best_path_score_key] = score


def get_best_path_score(
    position: tuple[int, ...], best_path_scores: dict[str, float]
) -> float | None:
    """Calculate and return the score for a given position.

    Args:
        position: A list of integers representing the position.

    Returns:
        The score as a float for the given position, None if not found.
    """
    if any(pos < 0 for pos in position):
        return constants.BEST_PATH_SCORE_BAD

    best_path_score_key = ",".join(str(pos) for pos in position)
    return best_path_scores.get(best_path_score_key)
