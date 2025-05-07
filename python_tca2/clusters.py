import json
from copy import deepcopy

from python_tca2.cluster import Cluster
from python_tca2.ref import Ref


class Clusters:
    def __init__(self) -> None:
        self.clusters: list[Cluster] = []  # list of Cluster

    def __str__(self) -> str:
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def to_json(self) -> dict:
        return {"clusters": [cluster.to_json() for cluster in self.clusters]}

    def create_and_add_cluster(
        self,
        ref1: Ref,
        ref2: Ref,
    ) -> None:
        """Adds two references to a new cluster and stores the cluster.

        This method creates a new cluster, adds the provided references to it,
        and then adds the cluster to the collection of clusters.

        Args:
            ref1 (Ref): The first reference to add to the cluster.
            ref2 (Ref): The second reference to add to the cluster.
        """
        new_cluster = Cluster()
        new_cluster.add_ref(ref1)
        new_cluster.add_ref(ref2)
        self.add_cluster(new_cluster)

    def add_ref(self, ref: Ref) -> None:
        """Adds a reference to the appropriate cluster or creates a new one.

        This method checks for clusters that match the given reference and merges
        them into a new cluster if overlaps are found. If no matching clusters
        exist, a new cluster is created with the reference.

        Args:
            ref: The reference to be added to a cluster.
        """
        overlaps = []
        for cluster in self.clusters:
            if cluster.matches(ref):
                overlaps.append(cluster)

        merged_cluster = Cluster()
        merged_cluster.add_ref(ref)

        for cluster in overlaps:
            if cluster.refs:
                merged_cluster.add_cluster(cluster)
                self.clusters.remove(cluster)

        self.clusters.append(merged_cluster)

    def add_clusters(self, other_clusters: "Clusters") -> None:
        """Add clusters from another Clusters object to the current instance.

        Args:
            other_clusters: The Clusters object containing the
                clusters to be added.
        """
        for other_cluster in other_clusters.clusters:
            self.add_cluster(other_cluster)

    @staticmethod
    def have_same_ref(cluster: Cluster, other_cluster: Cluster):
        """Check if two clusters share a common reference.

        Args:
            cluster: The first cluster to compare.
            other_cluster: The second cluster to compare.

        Returns:
            True if any reference in other_cluster matches the cluster, else False.
        """
        return any(cluster.matches(ref) for ref in other_cluster.refs)

    def add_cluster(self, other_cluster: Cluster) -> None:
        """Add a cluster to the current collection of clusters.

        This method identifies overlapping clusters based on reference similarity,
        merges them with the given cluster, and updates the collection by removing
        the old clusters and appending the merged one.

        Args:
            other_cluster: The cluster to be added and potentially merged.
        """
        overlaps: list[Cluster] = [
            cluster
            for cluster in self.clusters
            if self.have_same_ref(cluster, other_cluster)
        ]

        merged_cluster = deepcopy(other_cluster)

        for cluster in overlaps:
            if cluster.refs:
                merged_cluster.add_cluster(cluster)
                self.clusters.remove(cluster)

        self.clusters.append(merged_cluster)

    def get_score(self) -> float:
        """Calculate the total score for all clusters.

        Returns:
            The total score as a float.
        """
        return sum(cluster.get_score() for cluster in self.clusters)
