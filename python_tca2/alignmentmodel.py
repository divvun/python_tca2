import json
from typing import Iterator

from lxml import etree

from python_tca2 import alignment_suggestion, constants
from python_tca2.aelement import AlignmentElement
from python_tca2.aligned import Aligned
from python_tca2.aligned_sentence_elements import AlignedSentenceElements
from python_tca2.alignment_suggestion import AlignmentSuggestion
from python_tca2.anchorwordlist import AnchorWordList
from python_tca2.compare import Compare
from python_tca2.exceptions import (
    BlockedExceptionError,
    EndOfAllTextsExceptionError,
    EndOfTextExceptionError,
)
from python_tca2.paralleldocuments import ParallelDocuments
from python_tca2.queue_entries import QueueEntries
from python_tca2.queue_entry import QueueEntry


class AlignmentModel:
    special_characters = constants.DEFAULT_SPECIAL_CHARACTERS
    scoring_characters = constants.DEFAULT_SCORING_CHARACTERS
    max_path_length = constants.MAX_PATH_LENGTH

    def __init__(
        self,
        tree_tuple: tuple[etree._ElementTree, ...],
        anchor_word_list: AnchorWordList,
    ) -> None:
        self.anchor_word_list = anchor_word_list
        self.parallel_documents = ParallelDocuments(
            elements=tuple(
                self.load_sentences(text_number=text_number, tree=tree)
                for text_number, tree in enumerate(tree_tuple)
            )
        )

    def load_sentences(
        self, text_number: int, tree: etree._ElementTree
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
                text=" ".join(
                    [text for text in "".join(node.itertext()).split() if text.strip()]
                ),
                text_number=text_number,
                element_number=index,
            )
            for index, node in enumerate(tree.iter("s"))
        ]

    def suggest_without_gui(self) -> tuple[Aligned, Compare]:
        """Suggest alignments.

        This method performs text alignment by iteratively processing paths
        and updating alignment and comparison objects. It stops when alignment
        is complete or a predefined run limit is exceeded.

        Returns:
            A tuple containing the aligned object and the comparison object.
        """
        aligned = Aligned([])
        compare = Compare()

        while (
            alignment_suggestion := self.retrieve_alignment_suggestion(compare=compare)
        ) is not None:
            aligned.pickup(
                self.find_more_to_align_without_gui(
                    alignment_suggestion=alignment_suggestion
                )
            )

        print(
            json.dumps(compare.to_json(), indent=0, ensure_ascii=False),
            file=open("compare.json", "w"),
        )

        return aligned, compare

    def retrieve_alignment_suggestion(
        self, compare: Compare
    ) -> AlignmentSuggestion | None:

        queue_entries = self.lengthen_paths(compare=compare)

        if (
            len(queue_entries.entries) < constants.NUM_FILES
            and not queue_entries.entries[0].alignment_suggestions
        ):
            # When the length of the queue list is less than the number of files
            # and the first path in the queue list has no steps, then aligment
            # is done
            return None

        return self.select_best_alignment_suggestion(queue_entries)

    def find_more_to_align_without_gui(
        self, alignment_suggestion: tuple[int, ...]
    ) -> AlignedSentenceElements:
        """Extract a tuple of aligned sentences.

        Args:
            alignment_suggestion: Tells how many sentences should be extracted from the
                parallel documents.

        Returns:
            A tuple containing the text elements.
        """

        return AlignedSentenceElements(
            tuple(
                [
                    self.parallel_documents.get_next_element(text_number)
                    for _ in range(increment_number)
                ]
                for text_number, increment_number in enumerate(alignment_suggestion)
            )
        )

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

    def lengthen_paths(self, compare: Compare) -> QueueEntries:
        """Lengthens paths in a text pair alignment process.

        This method iteratively extends paths in the alignment model until no
        further extensions are possible or a maximum path length is reached.

        Args:
            compare: A comparison object used to evaluate path extensions.

        Returns:
            A QueueList containing the final set of extended paths.
        """
        best_path_scores: dict[str, float] = {}
        queue_entries = QueueEntries(
            [QueueEntry(position=self.parallel_documents.start_position)]
        )
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
        compare: Compare,
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
            len(self.parallel_documents.elements)
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
        position: list[int],
        alignment_suggestion: AlignmentSuggestion,
        compare: Compare,
    ) -> float:
        """Calculate the score for a given step at a specific position.

        Args:
            position: The current position in the alignment.
            step: The step to evaluate.
            compare: The comparison object providing cell values.

        Returns:
            The score for the specified step.
        """
        cell = compare.get_cell_values(
            nodes=self.parallel_documents.elements,
            position=position,
            alignment_suggestion=alignment_suggestion,
        )
        return cell.get_score()

    def make_longer_path(
        self,
        old_position: list[int],
        old_score: float,
        alignment_suggestions: list[AlignmentSuggestion],
        compare: Compare,
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
        try:
            position_step_score = self.get_step_score(
                old_position,
                alignment_suggestions[-1],
                compare=compare,
            )
        except EndOfAllTextsExceptionError:
            return QueueEntry(
                position=old_position,
                score=old_score,
                alignment_suggestions=alignment_suggestions[:-1],
                end=True,
            )

        except (EndOfTextExceptionError, BlockedExceptionError):
            return None

        new_position = [
            old_position[text_number] + alignment_suggestions[-1][text_number]
            for text_number in range(constants.NUM_FILES)
        ]
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
    position: list[int], score: float, best_path_scores: dict[str, float]
) -> None:
    """Sets the score for a specific position in the best path scores.

    Args:
        position: A list representing the position in the path.
        score: The score to assign to the specified position.
    """
    best_path_score_key = ",".join(str(pos) for pos in position)
    best_path_scores[best_path_score_key] = score


def get_best_path_score(
    position: list[int], best_path_scores: dict[str, float]
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
