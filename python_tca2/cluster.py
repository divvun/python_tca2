import json
from copy import deepcopy
from dataclasses import asdict

from python_tca2 import constants
from python_tca2.ref import Ref


class Cluster:
    def __init__(self) -> None:
        self.refs: list[Ref] = []

    def to_json(self) -> dict:
        return {"refs": [asdict(ref) for ref in self.refs]}

    def __str__(self) -> str:
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def clone(self) -> "Cluster":
        return deepcopy(self)

    def add_ref(self, other_ref: Ref) -> None:
        """Adds a reference to the cluster if it is not already present.

        Args:
            other_ref: The reference to be added to the cluster.
        """
        if other_ref not in self.refs:
            self.refs.append(other_ref)

    def matches(self, other_ref: Ref) -> bool:
        """Check if the given reference matches any reference in the collection.

        Args:
            other_ref: The reference to compare against the collection.

        Returns:
            True if a match is found, otherwise False.
        """
        return any(ref.matches(other_ref) for ref in self.refs)

    def add_cluster(self, other_cluster: "Cluster") -> None:
        """Merges another cluster into the current cluster.

        Args:
            other_cluster: The cluster to be merged into this one.
        """
        for other_ref in other_cluster.refs:
            self.add_ref(other_ref)

    def get_score(self) -> float:
        """Calculate the score for the cluster based on its characteristics.

        This method computes a score for the cluster by analyzing the number
        of unique positions in which references appear across multiple texts,
        and the weight of the cluster. The score is adjusted based on the
        smallest number of unique positions and a percentage factor for large
        clusters.

        Returns:
            The calculated score for the cluster.
        """
        cluster_weight = self.get_max_cluster_weight()
        low = min(
            [
                len({ref.pos for ref in self.refs if ref.is_in_text(text_number)})
                for text_number in range(constants.NUM_FILES)
            ]
        )

        return cluster_weight * (
            1 + ((low - 1) * constants.DEFAULT_LARGE_CLUSTER_SCORE_PERCENTAGE / 100.0)
        )

    def get_max_cluster_weight(self) -> float:
        """Get the maximum weight of references in the cluster.

        Returns:
            The biggest weight among the refs.
        """
        weights = [
            ref.weight
            for text_number in range(constants.NUM_FILES)
            for ref in self.refs
            if ref.is_in_text(text_number)
        ]

        return max(weights) if weights else 0.0

    def count_anchor_word_entries(self) -> int:
        """Counts unique anchor word entry types in the references.

        Iterates through the references (`self.refs`) and checks if each reference
        is an anchor word type and has a unique match type. Keeps track of unique
        match types and returns their count.

        Returns:
            int: The count of unique anchor word entry types.
        """
        anchor_word_entry_numbers = []
        for ref in self.refs:
            if (
                ref.type_anchor_word()
                and ref.match_type not in anchor_word_entry_numbers
            ):
                anchor_word_entry_numbers.append(ref.match_type)
        return len(anchor_word_entry_numbers)

    def get_words(self, include_match_type: bool) -> list[str]:
        """Generate a list of formatted word strings from the cluster.

        This method processes the cluster's references, sorts them by word, and
        formats them into strings based on match type and text number. The
        formatting includes optional match type prefixes, slashes for text
        number gaps, and commas for consecutive words in the same text.

        Args:
            include_match_type: Whether to include match type in the output.

        Returns:
            A list of formatted strings representing the cluster's words.
        """
        ret: list[str] = []
        sorted_cluster = self.clone()
        sorted_cluster.refs.sort(key=lambda ref: ref.word)
        prev_match_type = float("-inf")
        prev_t = -1
        ret_line = ""
        for ref in sorted_cluster.refs:
            first_in_curr_match_type = ref.match_type > prev_match_type
            if first_in_curr_match_type:
                if ret:
                    ret.append(ret_line)
                    ret_line = ""
                    prev_t = -1
                if include_match_type:
                    match_type = ref.match_type
                    temp = match_type + 1
                    ret_line += str(temp) + " "
            first_in_curr_text = ref.text_number > prev_t
            if first_in_curr_text:
                if first_in_curr_match_type:
                    num_slashes = ref.text_number - prev_t - 1
                    first_in_curr_match_type = False
                else:
                    num_slashes = ref.text_number - prev_t
                ret_line += "/" * num_slashes
            else:
                ret_line += ","
            ret_line += ref.word
            prev_t = ref.text_number
            prev_match_type = ref.match_type
        if ret_line:
            ret.append(ret_line)
        return ret
