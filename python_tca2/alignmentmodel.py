import json
from typing import Iterator

from python_tca2 import alignment_suggestion, constants
from python_tca2.aelement import AlignmentElement
from python_tca2.aligned import Aligned
from python_tca2.aligned_sentence_elements import AlignedSentenceElements
from python_tca2.alignment_suggestion import AlignmentSuggestion
from python_tca2.anchorwordlist import AnchorWordList
from python_tca2.elementinfotobecompared import ElementInfoToBeCompared
from python_tca2.queue_entries import QueueEntries
from python_tca2.queue_entry import QueueEntry


class AlignmentModel:
    scoring_characters = constants.DEFAULT_SCORING_CHARACTERS
    max_path_length = constants.MAX_PATH_LENGTH

    def __init__(
        self,
        text_pair: tuple[str, str],
        anchor_word_list: AnchorWordList,
    ) -> None:
        self.anchor_word_list = anchor_word_list
        self.parallel_documents = tuple(
            self.load_sentences(
                text_number=text_number,
                sentences=text.splitlines(),
            )
            for text_number, text in enumerate(text_pair)
        )

    def get_aligned_sentence_elements(
        self, start_position: tuple[int, ...], alignment_suggestion: AlignmentSuggestion
    ) -> AlignedSentenceElements:
        """Returns the next AlignmentElement object for the specified text number.

        Args:
            alignment_suggestion: How man elements to move in each text.

        Returns:
            A tuple of AlignmentElement objects for each text.
        """
        # TODO: fix the -1 issue
        return_tuple = tuple(
            alignment_elements[
                current_position
                + 1 : current_position
                + 1
                + number_of_elements  # + 1 here because first element starts at -1 …
            ]
            for (current_position, number_of_elements, alignment_elements) in zip(
                start_position,
                alignment_suggestion,
                self.parallel_documents,
                strict=True,
            )
        )

        return AlignedSentenceElements(return_tuple)

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

    def suggest_without_gui(self) -> tuple[Aligned, dict[str, ElementInfoToBeCompared]]:
        """Suggest alignments.

        This method performs text alignment by iteratively processing paths
        and updating alignment and comparison objects. It stops when alignment
        is complete or a predefined run limit is exceeded.

        Returns:
            A tuple containing the aligned object and the comparison object.
        """
        aligned = Aligned([])
        comparison_matrix: dict[str, ElementInfoToBeCompared] = {}

        start_position: tuple[int, ...] = (-1, -1)
        while (
            alignment_suggestion := self.retrieve_alignment_suggestion(
                compare=comparison_matrix, start_position=start_position
            )
        ) is not None:
            aligned.pickup(
                self.get_aligned_sentence_elements(
                    start_position=start_position,
                    alignment_suggestion=alignment_suggestion,
                )
            )
            start_position = tuple(
                current_position + alignment_increment
                for current_position, alignment_increment in zip(
                    start_position, alignment_suggestion, strict=True
                )
            )

        print(
            json.dumps(
                {
                    "matrix": {
                        key: comparison_matrix[key].to_json()
                        for key in sorted(comparison_matrix.keys())
                    },
                },
                indent=0,
                ensure_ascii=False,
            ),
            file=open("compare.json", "w"),
        )

        return aligned, comparison_matrix

    def retrieve_alignment_suggestion(
        self,
        compare: dict[str, ElementInfoToBeCompared],
        start_position: tuple[int, ...],
    ) -> AlignmentSuggestion | None:

        queue_entries = self.lengthen_paths(
            compare=compare, start_position=start_position
        )

        if (
            len(queue_entries.entries) < constants.NUM_FILES
            and not queue_entries.entries[0].alignment_suggestions
        ):
            # When the length of the queue list is less than the number of files
            # and the first path in the queue list has no steps, then aligment
            # is done
            return None

        return self.select_best_alignment_suggestion(queue_entries)

    def select_best_alignment_suggestion(
        self, queue_entries: QueueEntries
    ) -> AlignmentSuggestion | None:
        """Selects the best alignment suggestion based on normalized scores.

        This method evaluates each candidate entry in the provided queue list by
        calculating a normalized score, which is the candidate's score divided
        by the length of its path in sentences.

        It then selects the first step suggestion from the path with the highest
        normalized score.

        Args:
            queue_entries : A collection of candidate entries, where each entry
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
            for candidate_entry in queue_entries.entries
        ]

        return max(score_step_list, key=lambda x: x[0])[1] if score_step_list else None

    def lengthen_paths(
        self,
        compare: dict[str, ElementInfoToBeCompared],
        start_position: tuple[int, ...],
    ) -> QueueEntries:
        """Lengthens paths in a text pair alignment process.

        This method iteratively extends paths in the alignment model until no
        further extensions are possible or a maximum path length is reached.

        Args:
            compare: A comparison object used to evaluate path extensions.

        Returns:
            A QueueList containing the final set of extended paths.
        """
        best_path_scores: dict[str, float] = {}
        queue_entries = QueueEntries([QueueEntry(position=start_position)])
        for _ in range(self.max_path_length):
            next_queue_entries = QueueEntries([])
            for queue_entry in queue_entries.entries:
                if not queue_entry.end:
                    for new_queue_entry in self.lengthen_current_path(
                        queue_entry,
                        compare=compare,
                        best_path_scores=best_path_scores,
                    ):
                        if new_queue_entry is not None:
                            pos = new_queue_entry.position
                            queue_entries.entries = [
                                queue_entry
                                for queue_entry in queue_entries.entries
                                if not queue_entry.has_hit(pos)
                            ]
                            next_queue_entries.entries = [
                                queue_entry
                                for queue_entry in next_queue_entries.entries
                                if not queue_entry.has_hit(pos)
                            ]
                            if new_queue_entry not in next_queue_entries.entries:
                                next_queue_entries.entries.append(new_queue_entry)

            if not next_queue_entries.entries:
                return queue_entries

            queue_entries = next_queue_entries

        return queue_entries

    def lengthen_current_path(
        self,
        queue_entry: QueueEntry,
        compare: dict[str, ElementInfoToBeCompared],
        best_path_scores: dict[str, float],
    ) -> Iterator[QueueEntry | None]:
        """Extends the current path in the alignment process.

        This method iterates through a list of steps to attempt extending the
        current path represented by the given queue entry. It handles various
        exceptions to manage the end of texts or blocked paths.

        Args:
            queue_entry: The current queue entry to be extended.
            queue_entries: The list of current queue entries.
            next_queue_entries: The list of queue entries for the next iteration.
            compare: A comparison object used during path extension.

        Yields:
            QueueEntry: A new queue entry representing the extended path or None if
                the path cannot be extended further.
        """
        for step in alignment_suggestion.generate_alignment_suggestions(
            len(self.parallel_documents)
        ):
            yield self.make_longer_path(
                old_position=queue_entry.position,
                old_score=queue_entry.score,
                alignment_suggestions=queue_entry.alignment_suggestions + [step],
                compare=compare,
                best_path_scores=best_path_scores,
            )

    def get_step_score(
        self,
        position: tuple[int, ...],
        alignment_suggestion: AlignmentSuggestion,
        compare: dict[str, ElementInfoToBeCompared],
    ) -> float:
        """Calculate the score for a given step at a specific position.

        Args:
            position: The current position in the alignment.
            step: The step to evaluate.
            compare: The comparison object providing cell values.

        Returns:
            The score for the specified step.
        """
        key = ",".join(
            [
                str(position[text_number] + 1)
                for text_number in range(constants.NUM_FILES)
            ]
            + [
                str(position[text_number] + alignment_suggestion[text_number])
                for text_number in range(constants.NUM_FILES)
            ]
        )

        if key not in compare:
            compare[key] = ElementInfoToBeCompared(
                aligned_sentence_elements=self.get_aligned_sentence_elements(
                    start_position=position,
                    alignment_suggestion=alignment_suggestion,
                ),
            )

        return compare[key].get_score()

    def will_reach_both_ends(self, position: tuple[int, ...]) -> bool:
        """Check if the current position will reach the end of the texts.

        Args:
            position: The current position in the alignment.

        Returns:
            True if the end of the texts are reached, False otherwise.
        """
        return all(
            current_position + 1 > len(n)
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
            current_position + 1 > len(n)
            for current_position, n in zip(
                position,
                self.parallel_documents,
                strict=True,
            )
        )

    def make_longer_path(
        self,
        old_position: tuple[int, ...],
        old_score: float,
        alignment_suggestions: list[AlignmentSuggestion],
        compare: dict[str, ElementInfoToBeCompared],
        best_path_scores: dict[str, float],
    ) -> QueueEntry | None:
        """Extend a path with a new step and update its score.

        Args:
            ret_queue_entry: The current queue entry containing the path and score.
            alignment_suggestion: The new alignement suggestion to add to the path.
            compare: An object used to compare and update scores.

        Returns:
            The updated queue entry if the new score is better, otherwise None.
        """
        new_position = tuple(
            position + alignment_step
            for position, alignment_step in zip(
                old_position,
                alignment_suggestions[-1],
                strict=True,
            )
        )

        if self.will_reach_both_ends(new_position):
            return QueueEntry(
                position=old_position,
                score=old_score,
                alignment_suggestions=alignment_suggestions[:-1],
                end=True,
            )

        if self.will_reach_one_end(new_position):
            return None

        position_step_score = self.get_step_score(
            old_position,
            alignment_suggestions[-1],
            compare=compare,
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

        return QueueEntry(
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
