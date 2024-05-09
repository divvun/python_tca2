import json
from copy import deepcopy
from typing import List

from python_tca2.cluster import Cluster
from python_tca2.ref import Ref


class Clusters:
    def __init__(self):
        self.clusters: List[Cluster] = []  # list of Cluster

    def __str__(self):
        return json.dumps(self.to_json(), indent=0, ensure_ascii=False)

    def to_json(self):
        return {"clusters": [cluster.to_json() for cluster in self.clusters]}

    def add(
        self,
        ref1: Ref,
        ref2: Ref,
    ):
        new_cluster = Cluster()
        new_cluster.add(ref1)
        new_cluster.add(ref2)
        self.add_cluster(new_cluster)

    def add_ref(self, ref: Ref):
        overlaps = []
        for cluster in self.clusters:
            if cluster.matches(ref):
                overlaps.append(cluster)

        merged_cluster = Cluster()
        merged_cluster.add(ref)

        for cluster in overlaps:
            if cluster.refs:
                merged_cluster.add_cluster(cluster)
                self.clusters.remove(cluster)

        self.clusters.append(merged_cluster)

    def add_clusters(self, other_clusters):
        for other_cluster in other_clusters.clusters:
            self.add_cluster(other_cluster)

    @staticmethod
    def have_same_ref(cluster: Cluster, other_cluster: Cluster):
        for ref in other_cluster.refs:
            if cluster.matches(ref):
                return True
        return False

    def add_cluster(self, other_cluster: Cluster):
        overlaps: Cluster = [
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

    def get_score(self, large_cluster_score_percentage: int) -> float:
        score = 0.0
        for cluster in self.clusters:
            score += cluster.get_score(large_cluster_score_percentage)

        return score
