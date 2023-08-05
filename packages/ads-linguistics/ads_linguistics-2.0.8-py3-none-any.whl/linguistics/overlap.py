import numpy as np
import pandas as pd
from gensim.matutils import corpus2csc
from linguistics.dictionary import Dictionary
from linguistics.pickle import Pickle
from tqdm import tqdm


class Overlap:

    def __init__(self):
        self.dct = ""
        self.term_doct_mat = ""
        self.overlap = ""
        self.norm_overlap = ""
        self.smarter_corpus = ""

    def create(self, filename):

        # additional_keywords = ["game_of_thrones"]
        # for word in additional_keywords:
        #     keywords.append(word)
        self.smarter_corpus = Pickle().read(filename)
        self.dct = Dictionary()
        self.dct.read(filename)
        bow_corpus = [self.dct.dct.doc2bow(set(line))
                      for line in self.smarter_corpus]
        self.term_doc_mat = corpus2csc(bow_corpus)

        term_term_mat = np.dot(self.term_doc_mat, self.term_doc_mat.T)

        self.overlap = pd.DataFrame(term_term_mat.todense())
        new_columns = [self.dct.dct.get(x)
                       for x in self.overlap.columns.values]
        self.overlap.index = new_columns
        self.overlap.columns = new_columns
        self.overlap = self.overlap.reset_index().rename(
            columns={"index": "id"})

    def save(self, filename):
        self.overlap.to_csv(filename + '_overlap.csv', index=False)

    def normalise(self, filename):
        words = self.overlap.set_index("id").columns
        overlap_temp = self.overlap.set_index("id")
        self.norm_overlap = pd.DataFrame()
        for i in tqdm(range(len(words))):
            for j in range(len(words)):
                self.norm_overlap.loc[words[i], words[j]] = overlap_temp.loc[words[i], words[j]]/(
                    self.dct.dct.dfs[self.dct.dct.token2id[words[j]]])
                + overlap_temp.loc[words[j], words[i]] / \
                    (self.dct.dct.dfs[self.dct.dct.token2id[words[i]]])
                -2*self.dct.dct.dfs[self.dct.dct.token2id[words[j]]
                                    ]/len(self.smarter_corpus)

        self.norm_overlap.reset_index().rename(columns={"index": "id"}).to_csv(
            filename + '_overlap_new.csv', index=False)
