import json
from collections import defaultdict
from copy import deepcopy

from python_tca2 import constants
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
from python_tca2.pathstep import PathStep
from python_tca2.queue_entry import QueueEntry
from python_tca2.queuelist import QueueList
from python_tca2.toalign import ToAlign
from python_tca2.unaligned import Unaligned


class AlignmentModel:
    special_characters = constants.DEFAULT_SPECIAL_CHARACTERS
    scoring_characters = constants.DEFAULT_SCORING_CHARACTERS
    max_path_length = constants.MAX_PATH_LENGTH

    def __init__(self, keys: list[int]):
        self.keys = keys
        self.nodes = []
        self.aligned = Aligned()
        self.to_align = ToAlign(defaultdict(list))
        self.compare = Compare()
        self.anchor_word_list = AnchorWordList()

    def load_trees(self, trees):
        self.unaligned = Unaligned(
            elements={
                index: self.load_tree(tree)
                for index, tree in enumerate(trees)
            }
        )

    def load_tree(self, tree) -> list[AElement]:
        self.nodes.append(tree.xpath("//s"))
        return [
            AElement(
                " ".join(
                    [text for text in "".join(node.itertext()).split() if text.strip()]
                ),
                index,
            )
            for index, node in enumerate(tree.iter("s"))
        ]

    def suggets_without_gui(self):
        run_limit = constants.RUN_LIMIT
        run_count = 0
        done_aligning = False

        while not done_aligning:
            print(f"run_count = {run_count}")
            self.compare.reset_best_path_scores()

            queue_list = self.lengthen_paths()

            if (
                len(queue_list.entry) < constants.NUM_FILES
                and not queue_list.entry[0].path.steps
            ):
                # When the length of the queue list is less than the number of files
                # and the first path in the queue list has no steps, then aligment
                # is done
                done_aligning = True
            else:
                print(f"queueList.entry.size() = {len(queue_list.entry)}")
                best_path = self.get_best_path(queue_list)

                if best_path and best_path.steps:
                    print(f"bestPath.steps.size() = {len(best_path.steps)}")
                    self.find_more_to_align_without_gui(best_path)
                    run_count += 1
                    done_aligning = run_count >= run_limit

                    if not done_aligning:
                        print("flushing")
                        self.flush_aligned_without_gui()
                    else:
                        print_frame("done_aligning run_limit exceeded")
                else:
                    done_aligning = True
        print(
            json.dumps(self.compare.to_json(), indent=0, ensure_ascii=False),
            file=open("compare.json", "w"),
        )

    def flush_aligned_without_gui(self):
        self.aligned.pickup(self.to_align.flush())

    def find_more_to_align_without_gui(self, best_path):
        step_suggestion = best_path.steps[0]
        for t in self.unaligned.elements.keys():
            i = 0
            while i < step_suggestion.increment[t]:
                self.to_align.pickup(t, self.unaligned.pop(t))
                i += 1
        return step_suggestion

    def get_best_path(self, queue_list):
        normalised_best_score = constants.BEST_PATH_SCORE_NOT_CALCULATED

        print(f"gbp {normalised_best_score}")
        best_path = None
        for candidate in queue_list.entry:
            print(
                f"gbp candidate = {candidate.score} {candidate.path.get_length_in_sentences()}"
            )
            normalised_candidate_score = (
                candidate.score / candidate.path.get_length_in_sentences()
            )
            print(f"gbp normalizedCandidateScore = {normalised_candidate_score}")
            if int(normalised_candidate_score * 100000) > int(
                normalised_best_score * 100000
            ):
                normalised_best_score = normalised_candidate_score
                print(f"gbp normalizedBestScore = {normalised_best_score} {candidate}")
                best_path = candidate.path

        print(f"gbp bestPath = {best_path}")
        return best_path

    def lengthen_paths(self):
        position = self.find_start_position()
        queue_list = QueueList()
        queue_list.add(QueueEntry(position, 0))
        step_count = 0
        done_lengthening = False
        while not done_lengthening:
            print(f"step_count = {step_count}")
            next_queue_list = QueueList()
            for x, queue_entry in enumerate(queue_list.entry):
                print(f"lp1 {step_count}")
                if not queue_entry.removed and not queue_entry.end:
                    print(f"lp2 {step_count} {queue_entry}")
                    self.lengthen_current_path(queue_entry, queue_list, next_queue_list)
            print(f"1 next.size {len(next_queue_list.entry)}")
            next_queue_list.remove_for_real()
            print(f"2 next.size {len(next_queue_list.entry)}")
            if next_queue_list.empty():
                print(f"lp3 {step_count}")
                done_lengthening = True
            else:
                print(f"lp4 {step_count}, {len(next_queue_list.entry)}")
                queue_list = next_queue_list
                step_count += 1
                done_lengthening = step_count >= self.max_path_length

        print(f"3 next.size {len(queue_list.entry)}")
        return queue_list

    def lengthen_current_path(
        self, queue_entry: QueueEntry, queue_list: QueueList, next_queue_list: QueueList
    ):
        for step in self.compare.step_list:
            try:
                print(
                    f"step = {step}".replace("{", "[")
                    .replace("}", "]")
                    .replace(",", ", ")
                )
                print("1 queueEntry")
                new_queue_entry = self.make_longer_path(deepcopy(queue_entry), step)
                if new_queue_entry.path is not None:
                    pos = new_queue_entry.path.position
                    queue_list.remove(pos)
                    next_queue_list.remove(pos)
                    print("2 queueEntry")
                    next_queue_list.add(new_queue_entry)
            except EndOfAllTextsExceptionError:
                new_queue_entry = deepcopy(queue_entry)
                print("3 queueEntry")
                new_queue_entry.end = True
                if not next_queue_list.contains(new_queue_entry):
                    print("4 queueEntry")
                    next_queue_list.add(new_queue_entry)
            except EndOfTextExceptionError:
                print("lcp EndOfTextException")
                pass
            except BlockedExceptionError:
                print("lcp BlockedException")
                pass

    def get_step_score(self, position, step):
        cell = self.compare.get_cell_values(self, position, step)
        return cell.get_score()

    def make_longer_path(self, ret_queue_entry, new_step: PathStep):
        print("1score")
        new_score = ret_queue_entry.score + self.get_step_score(
            ret_queue_entry.path.position, new_step
        )
        print("2score")
        ret_queue_entry.score = new_score
        ret_queue_entry.path.extend(new_step)

        print(
            f"2.1score {int(ret_queue_entry.score * 100000)} "
            f"{int(
            self.compare.get_score(ret_queue_entry.path.position) * 100000
        )}"
        )
        if int(ret_queue_entry.score * 100000) > int(
            self.compare.get_score(ret_queue_entry.path.position) * 100000
        ):
            print("3score")
            self.compare.set_score(ret_queue_entry.path.position, ret_queue_entry.score)
            return ret_queue_entry
        else:
            print("4score")
            ret_queue_entry.path = None
            return ret_queue_entry

    def find_start_position(self):
        position = [0] * constants.NUM_FILES
        for t in self.unaligned.elements.keys():
            if len(self.unaligned.elements[t]) > 0:
                first_unaligned = self.unaligned.elements[t][0]
                position[t] = first_unaligned.element_number - 1
            else:
                position[t] = len(self.nodes[t]) - 1

        return position

    def save_plain(self):
        for t in self.unaligned.elements.keys():
            self.save_new_line_format_file(f"aligned_{t}.txt", t)

    def save_new_line_format_file(self, filename, t: int):
        with open(filename, "w") as f:
            print(
                "\n".join(
                    [
                        " ".join(
                            [element.text for element in alignments_etc.elements[t]]
                        )
                        for alignments_etc in self.aligned.alignments
                    ]
                ),
                file=f,
            )
