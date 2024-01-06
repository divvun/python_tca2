from copy import deepcopy
from typing import List

from python_tca2.cluster import Cluster
from python_tca2.ref import Ref


class Clusters:
    def __init__(self):
        # print_frame()
        self.clusters: List[Cluster] = []  # list of Cluster

    def __str__(self):
        return f"clusters: {',\n'.join(str(cluster) for cluster in self.clusters)}"

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
        print(
            "add",
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
        )
        new_cluster = Cluster()
        new_cluster.add(Ref(match_type, weight, t, element_number1, pos1, len1, word1))
        new_cluster.add(Ref(match_type, weight, tt, element_number2, pos2, len2, word2))
        self.add_cluster(new_cluster)

    def add_ref(self, ref: Ref):
        print("make a new cluster from the new word reference")
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
        print("merge two Clusters")
        for other_cluster in other_clusters.clusters:
            self.add_cluster(other_cluster)

    @staticmethod
    def have_same_ref(cluster: Cluster, other_cluster: Cluster):
        print(f"have_same_ref: {cluster} {other_cluster}")
        for ref in other_cluster.refs:
            if cluster.matches(ref):
                return True
        return False

    def add_cluster(self, other_cluster: Cluster):
        print("add a Cluster to Clusters")
        overlaps: Cluster = [
            cluster
            for cluster in self.clusters
            if self.have_same_ref(cluster, other_cluster)
        ]
        print(f"overlaps: {len(overlaps)}")
        merged_cluster = deepcopy(other_cluster)

        for cluster in overlaps:
            merged_cluster.add_cluster(cluster)
            self.clusters.remove(cluster)
        print(f"mergedCluster: {merged_cluster} {len(self.clusters)}")
        self.clusters.append(merged_cluster)
        print(f"self.clusters: {len(self.clusters)}")

    def get_score(self, large_cluster_score_percentage):
        print("1 cl score", large_cluster_score_percentage, len(self.clusters))
        score = 0.0
        for cluster in self.clusters:
            score += cluster.get_score(large_cluster_score_percentage)
        print("2 cl score", score)

        return score
