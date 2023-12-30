from lxml import etree

from python_tca2 import constants
from python_tca2.aelement import AElement
from python_tca2.aligned import Aligned
from python_tca2.alignment_utils import print_frame
from python_tca2.anchorwordlist import AnchorWordList
from python_tca2.compare import Compare
from python_tca2.matchinfo import MatchInfo
from python_tca2.queuelist import QueueList
from python_tca2.toalign import ToAlign
from python_tca2.unaligned import Unaligned


class AlignmentModel:
    special_characters = constants.DEFAULT_SPECIAL_CHARACTERS
    scoring_characters = constants.DEFAULT_SCORING_CHARACTERS
    max_path_length = constants.MAX_PATH_LENGTH
    length_ratio = constants.DEFAULT_LENGTH_RATIO
    large_cluster_score_percentage = constants.DEFAULT_LARGE_CLUSTER_SCORE_PERCENTAGE
    docs = []
    nodes = []
    all_nodes = []
    aligned = Aligned()
    to_align = ToAlign()
    unaligned = Unaligned()
    compare = Compare()

    def __init__(self):
        print_frame()
        self.anchor_word_list = AnchorWordList(self)
        self.match_info = MatchInfo(self)

    def load_text(self, text_file, t):
        print_frame()
        # TODO: Add text file name to the model
        tree = etree.parse(text_file)
        self.docs.append(tree)
        self.nodes.append(tree.xpath("//s"))
        self.all_nodes.append(tree.xpath("//s"))

        for index, node in enumerate(tree.iter("s")):
            element = AElement(node, index)
            self.unaligned.add(element, t)

    def suggets_without_gui(self):
        mode = constants.MODE_AUTO
        print_frame()
        run_limit = constants.RUN_LIMIT
        run_count = 0
        done_aligning = False

        while not done_aligning:
            print_frame()
            self.compare.reset_best_path_scores()
            queue_list = self.lengthen_paths()

            if (
                len(queue_list.entry) < constants.NUM_FILES
                and not queue_list.entry[0].path.steps
            ):
                #     # When the length of the queue list is less than the number of files
                #     # and the first path in the queue list has no steps, then aligment
                #     # is done
                done_aligning = True
            else:
                print_frame("still looking for more to align")
                best_path = self.get_best_path(queue_list)

                if best_path.steps:
                    print_frame("best_path.steps")
                    run_count += 1
                    done_aligning = run_count >= run_limit

                    if not done_aligning:
                        self.flush_aligned_without_gui()
                else:
                    done_aligning = True

    def flush_aligned_without_gui(self):
        print_frame()
        self.aligned.pickup(self.to_align.flush())

    def find_more_to_align_without_gui(self, best_path):
        print_frame()
        step_suggestion = best_path.steps[0]
        for t in range(constants.NUM_FILES):
            i = 0
            while i < step_suggestion.increment[t]:
                self.to_align.pickup(t, self.unaligned.pop(t))
                i += 1
        return step_suggestion

    def get_best_path(self, queue_list):
        print_frame()
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
        print_frame()
        position = self.find_start_position()
        queue_list = QueueList(self, position)
        step_count = 0
        done_lengthening = False
        while not done_lengthening:
            next_queue_list = QueueList(self, position)
            for queue_entry in queue_list.entry:
            print_frame(
                len(queue_list.entry),
                len(next_queue_list.entry),
            )
                if not queue_entry.removed and not queue_entry.end:
                    self.lengthen_current_path(queue_entry, queue_list, next_queue_list)
            print_frame(len(next_queue_list.entry))
            next_queue_list.remove_for_real()
            if next_queue_list.empty():
                print_frame("next_queue_list.empty()")
                done_lengthening = True
            else:
                print_frame("next_queue_list.empty() is False")
                queue_list = next_queue_list
                step_count += 1
                done_lengthening = step_count >= self.max_path_length

        return queue_list

    def lengthen_current_path(self, queue_entry, queue_list, next_queue_list):
        for step in self.compare.step_list:
            if not queue_entry.removed and not queue_entry.end:
            print_frame(step)
                new_queue_entry = queue_entry.make_longer_path(self, step)
                if new_queue_entry.path is not None:
                    pos = new_queue_entry.path.position
                    queue_list.remove(pos)
                    next_queue_list.remove(pos)
                    next_queue_list.add(new_queue_entry)
                print_frame("EndOfAllTextsException")

    def find_start_position(self):
        position = [] * alignment.NUM_FILES
        print_frame()
        for t in range(constants.NUM_FILES):
            if len(self.unaligned.elements[t]) > 0:
                first_unaligned = self.unaligned.elements[t][0]
                position[t] = first_unaligned.element_number - 1
            else:
                position[t] = len(self.nodes[t]) - 1

        return position

    def save_plain(self):
        print("save_plain")
        for t in range(constants.NUM_FILES):
            self.save_new_line_format_file(t)

    def save_new_line_format_file(self, t):
        print_frame(t, len(self.aligned.elements[t]))
        for link in self.aligned.alignments:
            print(150, link)
            line = ""
            first = True
            for element_number in link.element_numbers:
                a_element = self.aligned.elements[t][element_number]
                element_text = a_element.text
                if first:
                    first = False
                else:
                    line += " "
                line += element_text
                print(160, line)
