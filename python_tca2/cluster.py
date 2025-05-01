import json
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
