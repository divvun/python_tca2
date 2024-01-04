from typing import List

from python_tca2 import alignment
from python_tca2.ref import Ref


class Cluster:
    def __init__(self):
        # print_frame()
        self.refs: List[Ref] = []

    def __str__(self):
        return "{\n" + f"refs: [\n{',\n'.join(self.refs)}\n]\n" + "}"

    def clone(self):
        # print_frame()
        return super().clone()

    def get_refs(self):
        # print_frame()
        return self.refs

    def add(self, other_ref):
        # print_frame()
        for ref in self.refs:
            if ref.exactly_matches(other_ref):
                return
        self.refs.append(other_ref)

    def matches(self, other_ref):
        # print_frame()
        for ref in self.refs:
            if ref.matches(other_ref):
                return True
        return False

    def add_cluster(self, other_cluster):
        # print_frame()
        for other_ref in other_cluster.refs:
            self.add(other_ref)

    def get_score(self, large_cluster_score_percentage):
        # print_frame()
        high = 0
        low = float("inf")
        cluster_weight = 0.0
        for t in range(alignment.NUM_FILES):
            count = 0
            positions = []
            for ref in self.refs:
                if ref.is_in_text(t):
                    if ref.get_pos() not in positions:
                        positions.append(ref.get_pos())
                    cluster_weight = max(cluster_weight, ref.get_weight())
                count = len(positions)
            low = min(low, count)
            high = max(high, count)
        print("1 cl2", high, low, cluster_weight)
        return cluster_weight * (
            1 + ((low - 1) * large_cluster_score_percentage / 100.0)
        )

    def count_anchor_word_entries(self):
        # print_frame()
        anchor_word_entry_numbers = []
        for ref in self.refs:
            if (
                ref.type_anchor_word()
                and ref.get_match_type() not in anchor_word_entry_numbers
            ):
                anchor_word_entry_numbers.append(ref.get_match_type())
        return len(anchor_word_entry_numbers)

    def get_words(self, include_match_type):
        # print_frame()
        ret = []
        sorted_cluster = self.clone()
        sorted_cluster.refs.sort(key=lambda ref: ref.get_word())
        prev_match_type = float("-inf")
        prev_t = -1
        ret_line = ""
        for ref in sorted_cluster.refs:
            first_in_curr_match_type = ref.get_match_type() > prev_match_type
            if first_in_curr_match_type:
                if ret:
                    ret.append(ret_line)
                    ret_line = ""
                    prev_t = -1
                if include_match_type:
                    match_type = ref.get_match_type()
                    temp = match_type + 1
                    ret_line += str(temp) + " "
            first_in_curr_text = ref.get_t() > prev_t
            if first_in_curr_text:
                if first_in_curr_match_type:
                    num_slashes = ref.get_t() - prev_t - 1
                    first_in_curr_match_type = False
                else:
                    num_slashes = ref.get_t() - prev_t
                ret_line += "/" * num_slashes
            else:
                ret_line += ","
            ret_line += ref.get_word()
            prev_t = ref.get_t()
            prev_match_type = ref.get_match_type()
        if ret_line:
            ret.append(ret_line)
        return ret
