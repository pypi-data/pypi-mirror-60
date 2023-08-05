import pandas as pd
import numpy as np
from linguistics.vectorise import Vectorise
from linguistics.io import io


class Utils:

    @staticmethod
    def compare_flare_to_dict(modelname, cutoff=200):
        w2v = Vectorise()
        w2v.load(modelname)
        flare = io.read_file(modelname + "_flare.csv")
        flare['size'].replace('', np.nan, inplace=True)
        flare.dropna(subset=['size'], inplace=True)
        keywords = list(flare.id)
        words = []
        for word, vocab_obj in w2v.model.wv.vocab.items():
            if vocab_obj.count < cutoff:
                continue
            if word in keywords:
                words.append(
                    {"word": word,
                     "count": vocab_obj.count,
                     "in_model": "True"})
            else:
                words.append(
                    {"word": word,
                     "count": vocab_obj.count,
                     "in_model": "False"})

        return pd.DataFrame(words)


    @staticmethod
    def meta_data(modelname, unit="s"):
        w2v = Vectorise()
        try:
            w2v.load(modelname)
            no_of_words = len(w2v.model.wv.vocab.keys())
        except Exception as e:
            print("No vectorise model yet")
            no_of_words = 0

        verbatim = io.read_file(modelname + ".csv")
        verbatim["datetime"] = pd.to_datetime(verbatim.created_utc, unit=unit)

        return {
            "posts": len(verbatim),
            "words": no_of_words,
            "start_date": verbatim.datetime.min(),
            "end_date": verbatim.datetime.max()
        }

