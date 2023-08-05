import hdbscan
import pandas as pd


class Cluster():
    def __init__(self, min_cluster_size=15, min_samples=1, alpha=1.0, cluster_selection_method='leaf'):
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self.alpha = alpha
        self.labels = []

    def fit(self, vectors):
        self.vectors = vectors
        self.algorithm = hdbscan.HDBSCAN(min_cluster_size=15, min_samples=1, alpha=1.00, cluster_selection_method='leaf').fit(vectors)

        clusters = pd.DataFrame({"label": self.algorithm.labels_}).reset_index()
        counts = clusters.label.value_counts().to_dict()
        good = {k: v for k, v in counts.items() if v < 1000}
        clusters["ok"] = clusters.label.apply(lambda x: x in good and x > -1)
        n_clusters = len(clusters.loc[clusters["ok"], "label"].unique())
        print("FOUND {} CLUSTERS".format(n_clusters))
        self.clusters = clusters
