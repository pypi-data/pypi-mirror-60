from gensim.corpora import Dictionary as Dict
from linguistics.pickle import Pickle
import os
from tqdm import tqdm
import pandas as pd
import numpy as np


class Dictionary():

    def __init__(self, corpus=None):
        if corpus is None:
            self.dct = None
        self.dct = Dict(corpus)
        self.keywords = []
        # bow_corpus = [dct.doc2bow(line) for line in smarter_corpus]
        # term_doc_mat = corpus2csc(bow_corpus)

        # saving

    def save(self, filename):
        if not os.path.exists("trained"):
            os.makedirs("trained")
        self.dct.save_as_text("trained/" + filename + ".DictSaved")

    def read(self, filename):
        self.dct = Dict.load_from_text("trained/" + filename + ".DictSaved")

    def reduce(self, filename):
        flare = pd.read_csv(filename + "_flare.csv")
        flare['size'].replace('', np.nan, inplace=True)
        flare.dropna(subset=['size'], inplace=True)

        self.keywords = list(flare.id)

        self.read(filename + "_full")

        corpus = Pickle().read(filename + "_full")

        smaller_corpus = []
        for sentence in tqdm(corpus):
            cleanups = [token.lower() for token in sentence if token in self.keywords]
            smaller_corpus.append(cleanups)

        self.dct = Dict(smaller_corpus)

        Pickle().save(smaller_corpus, filename)

        self.save(filename)
