from sklearn.decomposition import PCA, FastICA


class Decompose():

    def __init__(self, n_components=15, copy=True, whiten=True, mode="pca", max_iter=2000, model=None):
        if model is not None:
            self.model = model
        else:
            if mode == "pca":
                self.model = PCA(n_components=n_components, copy=copy, whiten=whiten)
            elif mode == "ica":
                self.model = FastICA(n_components=n_components, whiten=whiten, max_iter=max_iter)

    def fit(self, X):
        self.model.fit(X)

    def transform(self, X):
        return self.model.transform(X)

    def fit_transform(self, X):
        data = self.model.fit_transform(X)
        return data
