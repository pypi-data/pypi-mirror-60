# linguistics

## Introduction
Processes conversation data into vectors which are then clustered into themes. 


### Main Pipeline:
* Preprocess
* Vectorize
* Decompose
* Cluster

### Additional Functionality:
* Input Output
* Word Overlap
* Time Series Analysis


## Installation
This package utilizes various features and datasets from NLTK. Run the command below to install everything NLTK.
```
sudo python -m nltk.downloader -d /usr/local/share/nltk_data all
```

## Todo
* IO: ability to output an excel file for manually checking datasets with non-ascii characters (e.g. Turkish)
* Preprocessing: deaccent should be an optional argument ```gensim.utils.simple_preprocess(sentence, deacc=False)```
* Preprocessing: deduplicating on comment and user_name in order to not overrepresent 
* General: Config object that stores all the parameters used throughout the process (file_name, data size, language, deaccent ... number of clusters outputted etc.
* General: provide a string method to easily see state of a class e.g. ```def __str__(self): return '@{}'.format(self.n_components...)```
* Create a lemmatization dictionary ```{"run": ["running", "ran"]}```
* Create a safe_word_list for brands, products etc that we don't want to get lemmatized ```["brooks"]```
