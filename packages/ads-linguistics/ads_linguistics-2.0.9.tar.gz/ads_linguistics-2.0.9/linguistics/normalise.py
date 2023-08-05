from sklearn.preprocessing import normalize

class Normalise:

    @staticmethod
    def l2_norm(array):
        return normalize(array, norm='l2')

