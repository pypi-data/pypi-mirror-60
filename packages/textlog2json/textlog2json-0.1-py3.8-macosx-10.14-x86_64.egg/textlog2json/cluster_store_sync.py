from typing import List, Tuple
from textlog2json.lexer.cluster import Cluster
from textlog2json.cluster_storage import ClusterStorage

class ClusterStoreSync():
    """ Synchronize the changes of multiple cluster stores """

    def __init__(self, cs: ClusterStorage):
        self.cs = cs

    def sync(self, delta:Tuple):
        self._merge_modified_clusters(delta[0])
        self._add_new_clusters(delta[1])


    def _add_new_clusters(self, new_clusters: List[Cluster]):
        """ Add new clusters to cluster storage. Checking for duplicate inserts """

        for c in new_clusters:
            self.cs.processCluster(c, None)

    def _merge_modified_clusters(self, modified_clusters: List[Cluster]):
        """ Merge modified clusters into the cluster storage """

        for cluster in modified_clusters:
            if cluster.guid in self.cs.cluster_modified:
                self.cs.mergeClusters(self.cs.cluster_modified[cluster.guid], cluster)
            else:
                self.cs.mark_as_modified(cluster)
