from copy import deepcopy

from lxml import etree

from python_tca2 import constants
from python_tca2.aelement import AElement
from python_tca2.aligned import Aligned
from python_tca2.alignment_utils import print_frame
from python_tca2.anchorwordlist import AnchorWordList
from python_tca2.compare import Compare
from python_tca2.exceptions import EndOfAllTextsExceptionError, EndOfTextExceptionError
from python_tca2.pathstep import PathStep
from python_tca2.queue_entry import QueueEntry
from python_tca2.queuelist import QueueList
from python_tca2.toalign import ToAlign
from python_tca2.unaligned import Unaligned


class AlignmentModel:
    special_characters = constants.DEFAULT_SPECIAL_CHARACTERS
    scoring_characters = constants.DEFAULT_SCORING_CHARACTERS
    max_path_length = constants.MAX_PATH_LENGTH

    def __init__(self):
        self.docs = []
        self.nodes = []
        self.all_nodes = []
        self.aligned = Aligned()
        self.to_align = ToAlign()
        self.unaligned = Unaligned()
        self.compare = Compare()
        self.anchor_word_list = AnchorWordList(self)

        print(str(self.compare))

    def load_text(self, text_file, t):
        # print_frame()
        # TODO: Add text file name to the model
        tree = etree.parse(text_file)
        self.docs.append(tree)
        self.nodes.append(tree.xpath("//s"))
        self.all_nodes.append(tree.xpath("//s"))

        for index, node in enumerate(tree.iter("s")):
            element = AElement(node, index)
            self.unaligned.add(element, t)

    def suggets_without_gui(self):
        # print_frame()
        run_limit = 3  # constants.RUN_LIMIT
        run_count = 0
        done_aligning = False

        while not done_aligning:
            # print_frame("not done_aligning", run_count)
            self.compare.reset_best_path_scores()

            # Dette er anderledes enn i Java.
            # Her fanges EndOfAllTextsExceptionError i lengthen_paths()
            try:
                queue_list = self.lengthen_paths()
            except EndOfTextExceptionError:
                print_frame("EndOfTextExceptionError")
                break

            if (
                len(queue_list.entry) < constants.NUM_FILES
                and not queue_list.entry[0].path.steps
            ):
                print_frame("length done aligning")
                # When the length of the queue list is less than the number of files
                # and the first path in the queue list has no steps, then aligment
                # is done
                done_aligning = True
            else:
                # print_frame("still looking for more to align")
                best_path = self.get_best_path(queue_list)

                if best_path.steps:
                    step_suggestion = self.find_more_to_align_without_gui(best_path)
                    run_count += 1
                    done_aligning = run_count >= run_limit

                    if not done_aligning:
                        # print_frame("not done_aligning")
                        self.flush_aligned_without_gui()
                    else:
                        print_frame("done_aligning run_limit exceeded")
                else:
                    print_frame("no best_path.steps")
                    done_aligning = True

    def flush_aligned_without_gui(self):
        # print_frame()
        self.aligned.pickup(self.to_align.flush())

    def find_more_to_align_without_gui(self, best_path):
        # print_frame()
        step_suggestion = best_path.steps[0]
        for t in range(constants.NUM_FILES):
            print_frame(
                f"stepSuggestion.increment[{t}] = {step_suggestion.increment[t]}"
            )
            print_frame(self.unaligned.elements[t][0])
            print()
            i = 0
            while i < step_suggestion.increment[t]:
                self.to_align.pickup(t, self.unaligned.pop(t))
                i += 1
        return step_suggestion

    def get_best_path(self, queue_list):
        # print_frame()
        normalised_best_score = constants.BEST_PATH_SCORE_NOT_CALCULATED

        best_path = None
        for candidate in queue_list.entry:
            if not candidate.removed and not candidate.end:
                normalised_candidate_score = (
                    candidate.score / candidate.path.get_length_in_sentences()
                )
                if normalised_candidate_score > normalised_best_score:
                    normalised_best_score = normalised_candidate_score
                    best_path = candidate.path

        return best_path

    def lengthen_paths(self):
        # print_frame()
        position = self.find_start_position()
        queue_list = QueueList()
        queue_list.add(QueueEntry(position, 0))
        step_count = 0
        done_lengthening = False
        while not done_lengthening:
            print("step_count = " + str(step_count))
            next_queue_list = QueueList()
            # print_frame(
            #     len(queue_list.entry),
            #     len(next_queue_list.entry),
            # )
            for x, queue_entry in enumerate(queue_list.entry):
                if not queue_entry.removed and not queue_entry.end:
                    self.lengthen_current_path(queue_entry, queue_list, next_queue_list)
            # print_frame(len(queue_list.entry), len(next_queue_list.entry))
            next_queue_list.remove_for_real()
            if next_queue_list.empty():
                # print_frame("next_queue_list.empty()")
                done_lengthening = True
            else:
                queue_list = next_queue_list
                step_count += 1
                done_lengthening = step_count >= self.max_path_length
                # print_frame("next_queue_list.empty() is False", done_lengthening)

        return queue_list

    def lengthen_current_path(
        self, queue_entry: QueueEntry, queue_list: QueueList, next_queue_list: QueueList
    ):
        for step in self.compare.step_list:
            # print_frame(str(step))
            try:
                # print("step = " + str(step))
                # print("1 queueEntry " + str(queue_entry))
                new_queue_entry = self.make_longer_path(deepcopy(queue_entry), step)
                if new_queue_entry.path is not None:
                    pos = new_queue_entry.path.position
                    queue_list.remove(pos)
                    next_queue_list.remove(pos)
                    # print("2 queueEntry " + str(new_queue_entry))
                    next_queue_list.add(new_queue_entry)
            except EndOfAllTextsExceptionError:
                print_frame("EndOfAllTextsException")
                new_queue_entry = deepcopy(queue_entry)
                new_queue_entry.end = True
                if not next_queue_list.contains(new_queue_entry):
                    # print("3 queueEntry " + str(new_queue_entry))
                    next_queue_list.add(new_queue_entry)
            except EndOfTextExceptionError:
                # print_frame("EndOfTextException")
                break

    def get_step_score(self, position, step):
        # print_frame()
        print("getStepScore: step = " + str(step))
        print(f"position = {position[0]},{position[1]}")

        cell = self.compare.get_cell_values(self, position, step)
        return cell.get_score()

    def make_longer_path(self, ret_queue_entry, new_step: PathStep):
        # print_frame()
        position = ret_queue_entry.path.position
        print("Make longer path " + str(ret_queue_entry))
        print("step = " + str(new_step))
        print(f"position = {position[0]},{position[1]}")

        new_score = ret_queue_entry.score + self.get_step_score(
            ret_queue_entry.path.position, new_step
        )

        ret_queue_entry.score = new_score
        ret_queue_entry.path.extend(new_step)

        if ret_queue_entry.score > self.compare.get_score(
            ret_queue_entry.path.position
        ):
            self.compare.set_score(ret_queue_entry.path.position, ret_queue_entry.score)
            return ret_queue_entry
        else:
            ret_queue_entry.path = None
            return ret_queue_entry

    def find_start_position(self):
        # print_frame()
        position = [0] * constants.NUM_FILES
        for t in range(constants.NUM_FILES):
            if len(self.unaligned.elements[t]) > 0:
                first_unaligned = self.unaligned.elements[t][0]
                position[t] = first_unaligned.element_number - 1
            else:
                position[t] = len(self.nodes[t]) - 1

        return position

    def save_plain(self):
        # print_frame("save_plain")
        for t in range(constants.NUM_FILES):
            self.save_new_line_format_file(t)

    def save_new_line_format_file(self, t):
        with open(f"aligned_{t}.txt", "w") as f:
            print_frame(t, len(self.aligned.elements[t]), len(self.aligned.alignments))
            print(
                "\n".join(
                    [
                        " ".join(
                            [
                                self.aligned.elements[t][element_number].element.text
                                for element_number in link.element_numbers[t]
                            ]
                        )
                        for link in self.aligned.alignments
                    ]
                ),
                file=f,
            )
