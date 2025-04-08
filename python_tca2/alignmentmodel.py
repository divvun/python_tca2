import json
from collections import defaultdict
from copy import deepcopy

from lxml import etree

from python_tca2 import constants, steplist
from python_tca2.aelement import AlignmentElement
from python_tca2.aligned import Aligned
from python_tca2.alignment_utils import print_frame
from python_tca2.anchorwordlist import AnchorWordList
from python_tca2.compare import Compare
from python_tca2.exceptions import (
    BlockedExceptionError,
    EndOfAllTextsExceptionError,
    EndOfTextExceptionError,
)
from python_tca2.paralleldocuments import ParallelDocuments
from python_tca2.pathstep import PathStep
from python_tca2.queue_entries import QueueEntries
from python_tca2.queue_entry import QueueEntry
from python_tca2.tca2path import Tca2Path
from python_tca2.toalign import ToAlign


class AlignmentModel:
    special_characters = constants.DEFAULT_SPECIAL_CHARACTERS
    scoring_characters = constants.DEFAULT_SCORING_CHARACTERS
    max_path_length = constants.MAX_PATH_LENGTH

    def __init__(self, tree_dict: dict):
        self.keys = list(tree_dict.keys())
        self.anchor_word_list = AnchorWordList()
        self.parallel_documents = ParallelDocuments(
            elements=defaultdict(
                list,
                {index: self.load_sentences(tree) for index, tree in tree_dict.items()},
            )
        )

    def load_sentences(self, tree: etree._ElementTree) -> list[AlignmentElement]:
        """Extracts and processes sentences from an XML tree.

        Args:
            tree: An XML tree containing sentence elements.

        Returns:
            A list of AlignmentElement objects, each representing a sentence.
        """
        return [
            AlignmentElement(
                element_number=index,
                text=" ".join(
                    [text for text in "".join(node.itertext()).split() if text.strip()]
                ),
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
        compare = Compare(
            anchor_word_list=self.anchor_word_list,
            nodes=self.parallel_documents.elements,
        )

        for _ in range(constants.RUN_LIMIT):
            step_suggestion = self.get_step_suggestion(compare=compare)
            if step_suggestion is None:
                break

            to_align = self.find_more_to_align_without_gui(
                step_suggestion=step_suggestion
            )
            aligned.pickup(to_align.flush())
            compare.reset_best_path_scores()

        else:
            print_frame("run_limit exceeded")

        print(
            json.dumps(compare.to_json(), indent=0, ensure_ascii=False),
            file=open("compare.json", "w"),
        )

        return aligned, compare

    def get_step_suggestion(self, compare: Compare) -> PathStep | None:
        queue_entries = self.lengthen_paths(compare=compare)

        if (
            len(queue_entries.entries) < constants.NUM_FILES
            and not queue_entries.entries[0].path.steps
        ):
            # When the length of the queue list is less than the number of files
            # and the first path in the queue list has no steps, then aligment
            # is done
            return None

        return self.get_best_path(queue_entries)

    def find_more_to_align_without_gui(self, step_suggestion: PathStep) -> ToAlign:
        """Aligns more text elements.

        Args:
            step_suggestion: Contains the increment steps for alignment.

        Returns:
            A ToAlign object with the aligned text elements.
        """
        to_align = ToAlign(defaultdict(list))
        for text_number in self.keys:
            number_of_steps = 0
            while number_of_steps < step_suggestion.increment[text_number]:
                to_align.pickup(
                    text_number, self.parallel_documents.get_next_element(text_number)
                )
                number_of_steps += 1

        return to_align

    def get_best_path(self, queue_entries: QueueEntries) -> PathStep | None:
        """Selects the best path step based on normalized scores.

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
                candidate_entry.path.steps[0],
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
        queue_entries = QueueEntries([])
        queue_entries.add(
            QueueEntry(
                path=Tca2Path(initial_position=self.parallel_documents.start_position),
                score=0,
            )
        )
        for _ in range(self.max_path_length):
            next_queue_entries = QueueEntries([])
            for queue_entry in queue_entries.entries:
                if not queue_entry.removed and not queue_entry.end:
                    self.lengthen_current_path(
                        queue_entry, queue_entries, next_queue_entries, compare=compare
                    )
            next_queue_entries.remove_for_real()
            if next_queue_entries.empty():
                break

            queue_entries = next_queue_entries
        else:
            print_frame("max_path_length exceeded")

        return queue_entries

    def lengthen_current_path(
        self,
        queue_entry: QueueEntry,
        queue_entries: QueueEntries,
        next_queue_entries: QueueEntries,
        compare: Compare,
    ) -> None:
        """Extends the current path in the alignment process.

        This method iterates through a list of steps to attempt extending the
        current path represented by the given queue entry. It handles various
        exceptions to manage the end of texts or blocked paths.

        Args:
            queue_entry: The current queue entry to be extended.
            queue_entries: The list of current queue entries.
            next_queue_entries: The list of queue entries for the next iteration.
            compare: A comparison object used during path extension.

        Raises:
            EndOfAllTextsExceptionError: Indicates all texts have been processed.
            EndOfTextExceptionError: Indicates the end of a single text.
            BlockedExceptionError: Indicates a path is blocked.
        """
        for step in steplist.create_step_list(len(self.keys)):
            try:
                new_queue_entry = self.make_longer_path(
                    deepcopy(queue_entry), step, compare=compare
                )
                if new_queue_entry is not None and new_queue_entry.path is not None:
                    pos = new_queue_entry.path.position
                    queue_entries.remove(pos)
                    next_queue_entries.remove(pos)
                    next_queue_entries.add(new_queue_entry)
            except EndOfAllTextsExceptionError:
                new_queue_entry = deepcopy(queue_entry)
                new_queue_entry.end = True
                if not next_queue_entries.contains(new_queue_entry):
                    next_queue_entries.add(new_queue_entry)
            except EndOfTextExceptionError:
                pass
            except BlockedExceptionError:
                pass

    @staticmethod
    def get_step_score(position: list[int], step: PathStep, compare: Compare) -> float:
        """Calculate the score for a given step at a specific position.

        Args:
            position: The current position in the alignment.
            step: The step to evaluate.
            compare: The comparison object providing cell values.

        Returns:
            The score for the specified step.
        """
        cell = compare.get_cell_values(position, step)
        return cell.get_score()

    def make_longer_path(
        self, ret_queue_entry: QueueEntry, new_step: PathStep, compare: Compare
    ) -> QueueEntry | None:
        """Extend a path with a new step and update its score.

        Args:
            ret_queue_entry: The current queue entry containing the path and score.
            new_step: The new step to add to the path.
            compare: An object used to compare and update scores.

        Returns:
            The updated queue entry if the new score is better, otherwise None.
        """
        position_step_score = self.get_step_score(
            ret_queue_entry.path.position, new_step, compare=compare
        )
        new_score = ret_queue_entry.score + position_step_score

        ret_queue_entry.score = new_score
        ret_queue_entry.path.extend(new_step)

        if int(ret_queue_entry.score * 100000) > int(
            compare.get_score(ret_queue_entry.path.position) * 100000
        ):
            compare.set_score(ret_queue_entry.path.position, ret_queue_entry.score)
            return ret_queue_entry

        return None
