from typing import List

from python_tca2.cluster import Cluster
from python_tca2.ref import Ref


class Clusters:
    def __init__(self):
        self.clusters: List[Cluster] = []  # list of Cluster

    def add(
        self,
        match_type,
        weight,
        t,
        tt,
        element_number1,
        element_number2,
        pos1,
        pos2,
        len1,
        len2,
        word1,
        word2,
    ):
        new_cluster = Cluster()
        new_cluster.add(Ref(match_type, weight, t, element_number1, pos1, len1, word1))
        new_cluster.add(Ref(match_type, weight, tt, element_number2, pos2, len2, word2))
        self.clusters.append(new_cluster)

    def add_ref(self, ref):
        overlaps = []
        for cluster in self.clusters:
            if cluster.matches(ref):
                overlaps.append(cluster)

        merged_cluster = Cluster()
        merged_cluster.add(ref)

        for cluster in overlaps:
            merged_cluster.add(cluster)
            self.clusters.remove(cluster)

        self.clusters.append(merged_cluster)

    def add_clusters(self, other_clusters):
        for other_cluster in other_clusters.clusters:
            self.add_ref(other_cluster)

    def add_cluster(self, other_cluster):
        overlaps = []
        for cluster in self.clusters:
            if cluster.matches(other_cluster):
                overlaps.append(cluster)

        for cluster in overlaps:
            other_cluster.add(cluster)
            self.clusters.remove(cluster)

        self.clusters.append(other_cluster)
