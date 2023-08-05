import pickle
import os

class Pickle():

    @staticmethod
    def save(corpus, filename):
        if not os.path.exists("trained"):
            os.makedirs("trained")
        with open("trained/" + filename + '.tokenizer.pickle', 'wb') as handle:
            pickle.dump(corpus, handle, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def read(filename):
        with open("trained/" + filename + '.tokenizer.pickle', 'rb') as handle:
            corpus = pickle.load(handle)
        return corpus 