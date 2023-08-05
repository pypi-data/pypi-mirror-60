"""
# Dimensionality of the resulting word vectors.
num_features = 300

# Minimum word count threshold.
min_word_count = 8

# Number of threads to run in parallel.
num_workers = multiprocessing.cpu_count()

# Context window length.
context_size = 10

# Downsample setting for frequent words.
downsampling = 1e-3

# Seed for the RNG, to make the results reproducible.
seed = 1

"""
import os
import multiprocessing
import gensim.models.word2vec as w2v
import pandas as pd

class Vectorise:

    def __init__(self, num_features=300, min_word_count=8, 
            context_size=10, downsampling=1e-3, seed=1, model="w2v"):
            self.model_type = model
            if model == "w2v":
                self.model = w2v.Word2Vec(sg=0,  seed=seed, workers=multiprocessing.cpu_count(), size=num_features, min_count=min_word_count, window=context_size, sample=downsampling)

    def add_verbatim(self, sentences):
        if self.model_type == "w2v":
            self.model.build_vocab(sentences)


    def train(self, sentences):
        if self.model_type == "w2v":
            self.model.train(sentences, total_examples=self.model.corpus_count, epochs=self.model.iter)
            self.ordered_vocab = pd.DataFrame([{"word":term, "index":voc.index, "count":voc.count} for term, voc in self.model.wv.vocab.items()])

    def save(self, filename):
        if not os.path.exists("trained"):
            os.makedirs("trained")

        if self.model_type == "w2v":
            self.model.save(os.path.join("trained", filename + ".w2v"))

    def load(self, filename):

        if self.model_type == "w2v":
            self.model = w2v.Word2Vec.load(os.path.join("trained", filename + ".w2v"))

