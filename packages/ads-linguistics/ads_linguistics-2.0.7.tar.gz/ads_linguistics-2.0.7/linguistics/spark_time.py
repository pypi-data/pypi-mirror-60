import os
from linguistics.pickle import Pickle
from linguistics.dictionary import Dictionary
from tqdm import tqdm
import multiprocessing
from multiprocessing import Process
import glob
import pandas as pd
import numpy as np
from gensim.matutils import corpus2csc
from array_split import array_split, shape_split


class SparkTime:

    def __init__(self):
        self.frequency = "week"
        self.unit = "s"
        self.temp = "temp"
        if not os.path.exists(self.temp):
            os.makedirs(self.temp)
        for the_file in os.listdir(self.temp):
            file_path = os.path.join(self.temp, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)

    def add_keywords(self, filename):
        flare = pd.read_csv(filename + "_flare.csv")
        flare['size'].replace('', np.nan, inplace=True)
        flare.dropna(subset=['size'], inplace=True)

        self.keywords = list(flare.id)

        self.number_of_cores = multiprocessing.cpu_count()

    def create(self, filename):

        # additional_keywords = ["game_of_thrones"]
        # for word in additional_keywords:
        #     keywords.append(word)

        self.verbatim = pd.read_csv(
            filename + "_spark_sentence.csv").fillna('')
        self.verbatim["datetime"] = pd.to_datetime(
            self.verbatim["date"], unit=self.unit)
        smarter_corpus = Pickle().read(filename)
        self.dct = Dictionary()
        self.dct.read(filename)
        bow_corpus = [self.dct.dct.doc2bow(line) for line in smarter_corpus]
        self.term_doc_mat = corpus2csc(bow_corpus)

        list_of_ids = np.array(
            range(0, len(list(self.dct.dct.token2id.keys()))))

        self.list_of_lists = array_split(list_of_ids, self.number_of_cores)

    def set_frequency(self, freq="day"):
        if freq == "hour":
            self.verbatim['date'] = self.verbatim['datetime'].dt.strftime(
                '%Y-%m-%d-%H')
        elif freq == "day":
            self.verbatim['date'] = self.verbatim['datetime'].dt.strftime(
                '%Y-%m-%d')
        else:
            self.verbatim['date'] = self.verbatim['datetime'].dt.strftime(
                '%Y-%U')

    def do_pivot_init(self, i, df_temp):

        #   if keyword == "year-weeks" :
        #       return

        keyword = self.dct.dct.get(i)
        df_temp[keyword] = self.term_doc_mat.getrow(i).todense().T
        # df_temp = df_temp[(df_temp["yearweeks"]>'2017-01-01')&(df_temp["yearweeks"]<'2017-12-31')]
        pivot = pd.pivot_table(
            df_temp, values=df_temp.columns.values, index='yearweeks', aggfunc='sum')
        df_pivot = pivot.reset_index()
        df_pivot = df_pivot[df_pivot["yearweeks"] != "NaT"]
        df_pivot.to_csv(self.temp + "/" + keyword + '.csv', index=False)

        del df_temp[keyword]

    def sep_proc(self, index_range):
        df_temp = pd.DataFrame()
        df_temp['yearweeks'] = self.verbatim.date
        for i in tqdm(index_range):
            self.do_pivot_init(i, df_temp)

    def run(self):

        procs = []

        for list_of_ids in self.list_of_lists:
            proc = Process(target=self.sep_proc, args=([list_of_ids]))
            procs.append(proc)
            proc.start()

        for proc in procs:
            proc.join()

    def collate(self):
        list_ = []
        for file_ in glob.glob(self.temp + "/*.csv"):
            list_.append(pd.read_csv(file_, index_col='yearweeks'))

        self.frame = pd.concat(list_, axis=1)
        pivot_full_corpus = pd.pivot_table(
            self.verbatim, values="body", index="date", aggfunc="count")
        self.frame["fullCorpus"] = pivot_full_corpus["body"]

    def read(self, filename):
        self.frame = pd.read_csv(filename + '_spark_time.csv', index_col="yearweeks")

    def save(self, filename):
        self.frame.to_csv(filename + '_spark_time.csv')

    def rolling(self, filename, window=5):
        self._rolling = self.frame.rolling(window=window).mean()
        self._rolling = self._rolling.fillna(0)
        self._rolling.to_csv(filename + "_spark_time_avg.csv")

    def normalise(self, spark_time, filename=None):
        for col in spark_time.columns:
            spark_time[col] = spark_time[col]/spark_time["fullCorpus"]

        if filename is not None:
            spark_time.to_csv(filename + "spark_time_norm.csv")
        else:
            return spark_time
