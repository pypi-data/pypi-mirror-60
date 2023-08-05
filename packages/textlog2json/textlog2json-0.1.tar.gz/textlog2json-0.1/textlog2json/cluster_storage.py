""" Contains to storel and retrive clusters. Keeps that info in sync with an external db and across threads. """

import math
from textlog2json.lexer.parse import parse
from textlog2json.lexer.cluster import Cluster
from typing import List, Dict, Any, Tuple, Optional
from textlog2json.distance import distance
from collections import namedtuple
from re import compile

from textlog2json import pattern_format
from textlog2json import patternmatcher

REGEX_NAME_PREFIX = "textlog2json"

DuplicateID = namedtuple('DuplicateID', 'last_synced current_id')

class ClusterStorage():
    """ Stores and finds clusters and keeps clusters in sync with an external db """

    def __init__(self, distance_treshold: float):
        """ Connect to db and setup tables """

        self.distance_treshold = distance_treshold

        self._manual_matches_regexp = None
        self._manual_matches_guids = {}

        self.pattern_hash = ""
        self.cluster_dict = {}
        self.new_clusters = {}
        self.cluster_modified = {}
        self.cluster_deleted = {}
        self._keywords = {}
        self._keywords_reverse = {}

    def set_manual_matches_regexp(self, regexps: List[Tuple[str, str]]):
        """ Generate the manual matches regexp from a list of regexps and guids """

        self._manual_matches_guids = {}

        regexp = ''
        glue = ''
        i = 1
        for g, r in regexps:
            self._manual_matches_guids[g] = None
            regexp += glue + '(?P<' + REGEX_NAME_PREFIX + str(i) + '_' + g + '>' + r + ')'
            glue = '|'
            i += 1
        self._manual_matches_regexp = compile(regexp)

    def _find_cluster_by_regexp(self, msg:str) -> Optional[str]:
        """ Check if messages match a regex, if so get the corresponding guid """

        if not self._manual_matches_regexp is None:
            mg = self._manual_matches_regexp.search(msg)
            if mg and mg.lastgroup and mg.lastgroup.startswith(REGEX_NAME_PREFIX):
                pos = mg.lastgroup.find('_')
                if pos > 0:
                    guid = mg.lastgroup[pos+1:]
                    return guid
        return None

    def _check_if_manual_match(self, cluster:Cluster, msg:str):
        """ Check if the given msg matches a manual cluster, if so adapt the guid """

        guid = self._find_cluster_by_regexp(msg)
        if not guid is None:
            cluster.guid = guid

    def getDelta(self) -> Tuple:
        """ Get the modifications made to the cluster storage """
        return (list(self.cluster_modified.values()), list(self.new_clusters.values()))

    def processMsg(self, msg: str, msg_dict: Dict[str, Any]):
        """ Add message to an existing cluster or create a new one """

        rootToken = parse(msg)
        cluster = Cluster(rootToken.children)
        cluster.counter = 1
        self._check_if_manual_match(cluster, msg)
        self.processCluster(cluster, msg_dict)

    def deleteCluster(self, cluster: Cluster):
        """ Delete all occurences of given guid and mark it as deleted """

        self._keywords_unindex(cluster)

        if cluster.guid in self.cluster_dict:
            self.cluster_dict.pop(cluster.guid)
            if cluster.guid in self.cluster_modified:
                self.cluster_modified.pop(cluster.guid)

            if cluster.guid in self.new_clusters:
                self.new_clusters.pop(cluster.guid)
            else:
                self.cluster_deleted[cluster.guid] = None

    def mergeClusters(self, clusterA: Cluster, clusterB: Cluster):
        """ Merge the clusterB into clusterA """

        # Merge patterns
        clusterA.pattern = patternmatcher.MergePatterns(clusterA.pattern, clusterB.pattern)

        # Merge counter
        clusterA.counter += clusterB.counter

    def mark_as_modified(self, cluster: Cluster):
        """ Mark cluster as modified """

        self.cluster_dict[cluster.guid] = cluster

        # New clusters don't need to be marked as modified.
        if cluster.guid in self.new_clusters:
            self.new_clusters[cluster.guid] = cluster
        else:
            self.cluster_modified[cluster.guid] = cluster

    def processCluster(self, cluster: Cluster, msg_dict: Optional[Dict[str, Any]]):
        """ Process a pattern, find a cluster into which to put it, or create a new cluster """

        # Find clostest cluster and merge the new cluster into that.
        keyword_count = self.get_keyword_count(cluster)
        found_cluster = self.find(cluster, keyword_count)
        if not found_cluster is None:
            self.mergeClusters(found_cluster, cluster)
            self.mark_as_modified(found_cluster)

            # reindex cluster
            self._keywords_unindex(found_cluster)
            self.keywords_index(found_cluster, keyword_count)

            if not msg_dict is None:
                pattern_format.PatternValuesAddToDict(msg_dict, found_cluster.pattern)

                if not found_cluster.name is None:
                    msg_dict["cluster_name"] = found_cluster.name
            cluster = found_cluster
        else:
            self.cluster_dict[cluster.guid] = cluster
            self.new_clusters[cluster.guid] = cluster
            self.keywords_index(cluster, keyword_count)
        if not msg_dict is None:
            msg_dict["cluster_guid"] = cluster.guid

    def find(self, cluster: Cluster, keyword_count: List[Tuple[int, int]]):
        """ Find the closest cluster to the given cluster """

        if cluster.guid in self._manual_matches_guids:
            try:
                return self.cluster_dict[cluster.guid]
            except KeyError:
                return None

        pattern_length = len(cluster.pattern)
        min_matches = math.floor(pattern_length * (1-self.distance_treshold))

        for count, hash in keyword_count:
            if count != 0:
                for guid in self._keywords[hash]:
                    c = self.cluster_dict[guid]
                    if distance(c.pattern, cluster.pattern) <= min_matches:
                        return c

        return None

    def get_keyword_count(self, cluster: Cluster) -> List[Tuple[int, int]]:
        """ Count the number of times the keywords in a pattern are used """

        keyword_count = []
        for t in cluster.pattern:
            if len(t.children) == 0:
                hash = t.hash
            else:
                hash = -t.type

            count = 0
            try:
                count = len(self._keywords[hash])
            except KeyError:
                pass

            keyword_count.append((count, hash))

        return sorted(keyword_count)

    def keywords_index(self, cluster: Cluster, keyword_count: List[Tuple[int, int]]):
        """ Index the 50%+1 of keywords in a cluster that are the least frequently used """

        if not cluster.guid in self._manual_matches_guids:
            num_keywords_needed = math.floor(len(cluster.pattern) * (self.distance_treshold)) +1
            keywords = set()
            for count, hash in keyword_count[:num_keywords_needed]:
                keywords.add(hash)
                if count == 0:
                    self._keywords[hash] = set([cluster.guid])
                else:
                    self._keywords[hash].add(cluster.guid)
            self._keywords_reverse[cluster.guid] = keywords

    def _keywords_unindex(self, cluster: Cluster):
        """ Remove a cluster from the keyword index """

        try:
            for hash in self._keywords_reverse[cluster.guid]:
                try:
                    self._keywords[hash].remove(cluster.guid)
                except KeyError:
                    pass
            self._keywords_reverse.pop(cluster.guid)
        except KeyError:
            pass
