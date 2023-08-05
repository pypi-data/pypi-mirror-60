
import setuptools

setuptools.setup(
    name='ads_linguistics',
    version='2.0.8',
    description='The ADS Linguistic Library',
    url='https://flamingo-james-b@bitbucket.org/flamingodf/linguistics.git', author='Applied Data Science Team',
    author_email='james.burnett@flamingogroup.com',
    scripts=['bin/run_clusters', 'bin/create_all_files', 'bin/create_all_files_wo_dict', 'bin/compare_flare_to_dict', 'bin/get_meta',
             'bin/update_flare_counts'],
    license='Flamingo',
    packages=setuptools.find_packages(),
    install_requires=['array-split', 'gensim', 'hdbscan', 'nltk', 'pandas', 'scikit-learn', 'scipy',
                      'six' 'tqdm'],
    zip_safe=False)

# import nltk
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')
