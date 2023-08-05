import nltk
import gensim
from gensim.models import Phrases
import pandas as pd
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords, wordnet
from gensim.models.phrases import Phraser
from gensim.corpora import Dictionary
from tqdm import tqdm
import linguistics.gensim_utils as gensim_utils


tqdm.pandas()


class Preprocess:
    def __init__(self, data, model, lang, keep_words=[]):
        self.data = data
        self.lang = lang
        self.model = model
        self.keep_words = keep_words
        self._stopwords = stopwords.words(lang)
        self.new_data = pd.DataFrame()
        self.tokenizer = self.load_nltk_tokenizer()
        self.lemmatizer = WordNetLemmatizer()
        self.sentences = []
        self.tokenized_body = []

    def load_nltk_tokenizer(self):
        file_path = "tokenizers/punkt/{}.pickle".format(self.lang)
        try:
            tokenizer = nltk.data.load(file_path)
            return tokenizer
        except Exception as e:
            print("No tokenizer found for language = {}".format(self.lang))

    def set_frequency(self, freq="day"):
        if freq == "hour":
            self.new_data['datestring'] = self.new_data['datetime'].dt.strftime(
                '%Y-%m-%d-%H')
        elif freq == "day":
            self.new_data['datestring'] = self.new_data['datetime'].dt.strftime(
                '%Y-%m-%d')
        else:
            self.new_data['datestring'] = self.new_data['datetime'].dt.strftime(
                '%Y-%U')

    def create_sentences_dataframe(self):
        self.tokenized_body = self.data['body'].progress_apply(
            lambda x: self.tokenizer.tokenize(str(x).lower()))
        print("finished splitting")
        rows = []
        for i, row in tqdm(self.data.iterrows()):
            for a in self.tokenized_body[i]:
                row.sentence = a
                if "comment_id" in row.keys():
                    rows.append({"sentence": '"' + a + '"',
                                 "created_utc": row["created_utc"],
                                 "comment_id": row["comment_id"]})
                else:
                    rows.append({"sentence": '"' + a + '"',
                                 "created_utc": row["created_utc"]})
        self.new_data = pd.DataFrame(rows).fillna("")
        self.new_data["datetime"] = pd.to_datetime(self.new_data["created_utc"], unit="s")
        print(len(self.new_data))

    # Cleans and tokenizes each sentence in list (Lower cases words, removes stopwords/numbers etc.) sentences
    # is a list of lists containing cleaned words from each sentence in CSV.

    def clean_sentences(self, lemma=True):
        df = self.new_data
        sentences = []
        for sentence in tqdm(df.sentence.values):
            if len(sentence) > 0:
                pre_process = gensim_utils.simple_preprocess(
                    sentence, deacc=True)
                important_words = []
                for word in pre_process:
                    if word not in self._stopwords:
                        if lemma and word not in self.keep_words:
                            lemmatized_word = self.lemmatize_word(word)
                            important_words.append(lemmatized_word)
                        else:
                            important_words.append(word)
                sentences.append(important_words)
            else:
                sentences.append([])

        self.sentences = sentences

    def gram_it(self, min_count=5):
        phrases = Phrases(self.sentences, min_count=min_count)  # Train a model.
        bigram = Phraser(phrases)  # Exports the model.
        trigram = Phrases(bigram[self.sentences], min_count=min_count)  # Another training which yields any trigrams.
        tokenized_sentences = list((trigram[bigram[self.sentences]]))
        return tokenized_sentences

    def lemmatize_word(self, word):
        tag = self.get_wordnet_pos(word)
        lemmatized_word = self.lemmatizer.lemmatize(word, tag)
        return lemmatized_word

    @staticmethod
    def get_wordnet_pos(word):
        """Find a word's Part of Speech tag and map it a wordnet accepted form.
        https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
        """
        tag = nltk.pos_tag([word])[0][1][0]
        tag_dict = {
            "J": wordnet.ADJ,
            "N": wordnet.NOUN,
            "V": wordnet.VERB,
            "R": wordnet.ADV
        }

        tag = tag_dict.get(tag, wordnet.NOUN)  # Presume a word is a noun if it isn't in the above dict.
        return tag
