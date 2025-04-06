import json
from collections import defaultdict
from copy import deepcopy

from python_tca2 import constants, steplist
from python_tca2.aelement import AElement
from python_tca2.aligned import Aligned
from python_tca2.alignment_utils import print_frame
from python_tca2.anchorwordlist import AnchorWordList
from python_tca2.compare import Compare
from python_tca2.exceptions import (
    BlockedExceptionError,
    EndOfAllTextsExceptionError,
    EndOfTextExceptionError,
)
from python_tca2.path import Path
from python_tca2.pathstep import PathStep
from python_tca2.queue_entry import QueueEntry
from python_tca2.queuelist import QueueList
from python_tca2.textpair import TextPair
from python_tca2.toalign import ToAlign


class AlignmentModel:
    special_characters = constants.DEFAULT_SPECIAL_CHARACTERS
    scoring_characters = constants.DEFAULT_SCORING_CHARACTERS
    max_path_length = constants.MAX_PATH_LENGTH

    def __init__(self, tree_dict: dict):
        self.keys = list(tree_dict.keys())
        self.anchor_word_list = AnchorWordList()
        self.textpair = TextPair(
            elements=defaultdict(
                list, {index: self.load_tree(tree) for index, tree in tree_dict.items()}
            )
        )

    def load_tree(self, tree) -> list[AElement]:
        return [
            AElement(
                " ".join(
                    [text for text in "".join(node.itertext()).split() if text.strip()]
                ),
                index,
            )
            for index, node in enumerate(tree.iter("s"))
        ]

    def suggest_without_gui(self) -> tuple[Aligned, Compare]:
        run_limit = constants.RUN_LIMIT
        run_count = 0
        done_aligning = False
        aligned = Aligned([])
        compare = Compare(
            anchor_word_list=self.anchor_word_list, nodes=self.textpair.elements
        )

        while not done_aligning:
            compare.reset_best_path_scores()

            queue_list = self.lengthen_paths(compare=compare)

            if (
                len(queue_list.entries) < constants.NUM_FILES
                and not queue_list.entries[0].path.steps
            ):
                # When the length of the queue list is less than the number of files
                # and the first path in the queue list has no steps, then aligment
                # is done
                return aligned, compare
            else:
                step_suggestion = self.get_best_path(queue_list)

                if step_suggestion is not None:
                    to_align = self.find_more_to_align_without_gui(
                        step_suggestion=step_suggestion
                    )
                    run_count += 1
                    done_aligning = run_count >= run_limit

                    if not done_aligning:
                        aligned.pickup(to_align.flush())
                    else:
                        print_frame("done_aligning run_limit exceeded")
                else:
                    return aligned, compare
        print(
            json.dumps(compare.to_json(), indent=0, ensure_ascii=False),
            file=open("compare.json", "w"),
        )

        return aligned, compare

    def find_more_to_align_without_gui(self, step_suggestion):
        to_align = ToAlign(defaultdict(list))
        for text_number in self.keys:
            number_of_steps = 0
            while number_of_steps < step_suggestion.increment[text_number]:
                to_align.pickup(
                    text_number, self.textpair.get_next_element(text_number)
                )
                number_of_steps += 1

        return to_align

    def get_best_path(self, queue_list):
        normalised_best_score = constants.BEST_PATH_SCORE_NOT_CALCULATED

        step_suggestion = None
        for candidate_entry in queue_list.entries:
            normalised_candidate_score = (
                candidate_entry.score / candidate_entry.path.get_length_in_sentences()
            )
            if int(normalised_candidate_score * 100000) > int(
                normalised_best_score * 100000
            ):
                normalised_best_score = normalised_candidate_score
                if candidate_entry.path is not None and candidate_entry.path.steps:
                    step_suggestion = candidate_entry.path.steps[0]

        return step_suggestion

    def lengthen_paths(self, compare: Compare):
        queue_list = QueueList([])
        queue_list.add(QueueEntry(Path(self.textpair.start_position), 0))
        step_count = 0
        done_lengthening = False
        while not done_lengthening:
            next_queue_list = QueueList([])
            for queue_entry in queue_list.entries:
                if not queue_entry.removed and not queue_entry.end:
                    self.lengthen_current_path(
                        queue_entry, queue_list, next_queue_list, compare=compare
                    )
            next_queue_list.remove_for_real()
            if next_queue_list.empty():
                done_lengthening = True
            else:
                queue_list = next_queue_list
                step_count += 1
                done_lengthening = step_count >= self.max_path_length

        return queue_list

    def lengthen_current_path(
        self,
        queue_entry: QueueEntry,
        queue_list: QueueList,
        next_queue_list: QueueList,
        compare: Compare,
    ):
        for step in steplist.create_step_list(len(self.keys)):
            try:
                new_queue_entry = self.make_longer_path(
                    deepcopy(queue_entry), step, compare=compare
                )
                if new_queue_entry.path is not None:
                    pos = new_queue_entry.path.position
                    queue_list.remove(pos)
                    next_queue_list.remove(pos)
                    next_queue_list.add(new_queue_entry)
            except EndOfAllTextsExceptionError:
                new_queue_entry = deepcopy(queue_entry)
                new_queue_entry.end = True
                if not next_queue_list.contains(new_queue_entry):
                    next_queue_list.add(new_queue_entry)
            except EndOfTextExceptionError:
                pass
            except BlockedExceptionError:
                pass

    def get_step_score(self, position, step, compare: Compare):
        cell = compare.get_cell_values(position, step)
        return cell.get_score()

    def make_longer_path(self, ret_queue_entry, new_step: PathStep, compare: Compare):
        new_score = ret_queue_entry.score + self.get_step_score(
            ret_queue_entry.path.position, new_step, compare=compare
        )
        ret_queue_entry.score = new_score
        ret_queue_entry.path.extend(new_step)

        if int(ret_queue_entry.score * 100000) > int(
            compare.get_score(ret_queue_entry.path.position) * 100000
        ):
            compare.set_score(ret_queue_entry.path.position, ret_queue_entry.score)
            return ret_queue_entry
        else:
            ret_queue_entry.path = None
            return ret_queue_entry
