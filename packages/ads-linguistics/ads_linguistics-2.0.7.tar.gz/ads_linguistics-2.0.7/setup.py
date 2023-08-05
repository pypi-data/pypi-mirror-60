
import setuptools

setuptools.setup(
    name='ads_linguistics',
    version='2.0.7',
    description='The ADS Linguistic Library',
    url='https://flamingo-james-b@bitbucket.org/flamingodf/linguistics.git', author='Applied Data Science Team',
    author_email='james.burnett@flamingogroup.com',
    scripts=['bin/run_clusters', 'bin/create_all_files', 'bin/create_all_files_wo_dict', 'bin/compare_flare_to_dict', 'bin/get_meta',
             'bin/update_flare_counts'],
    license='Flamingo',
    packages=setuptools.find_packages(),
    install_requires=['array-split', 'boto', 'boto3', 'botocore', 'certifi', 'chardet', 'Cython', 'docutils', 'gensim', 'hdbscan', 'idna', 'jmespath',
                      'joblib', 'nltk', 'numpy', 'pandas', 'python-dateutil', 'pytz', 'requests', 's3transfer', 'scikit-learn', 'scipy',
                      'six', 'sklearn', 'smart-open', 'tqdm', 'urllib3'],
    zip_safe=False)

# import nltk
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')
