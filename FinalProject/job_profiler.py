"""
job_profiler.py
Lib to find similarities from input job profiles to existing job descriptions on the database.

Initialization goals:
- Read list of job descriptions
- Vectorize list job description using TF-IDF
- Store List of Vectorized job description

Usage goals:
- Receive Input Job Description
- Vectorize Input Job Description using TF-IDF
- Compare Input Job Description vector to stored List of Vectorized job description from using cosine similarity
- return top X simillar jobs.
"""

import pandas as pd
import numpy as np
import nltk
import json
import re
import pickle
import os

from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import linear_kernel

import spacy
import en_core_web_sm  # english model

# load English tokenizer, tagger, parser, NER and word vectors
nlp = en_core_web_sm.load()


# TODO: read json as Data Frame.
df = pd.read_csv('nlp/carry_on_df.csv')
# df = pd.read_json('career_builder_jobs_10501.json')
#lemmatized_csv = 'FinalProject/nlp/lemmatized_df_7.csv'
#df = pd.read_csv(lemmatized_csv)

# make a new tfidf mtx - we could also import, if desired.
corpus_tfidf_mtx_file = 'nlp/our_tfidf_mtx_8.pkl'
with open(corpus_tfidf_mtx_file, 'rb') as f:
    corpus_tfidf_mtx = pickle.load(f)
#corpus_tfidf = TfidfVectorizer(min_df=1, stop_words="english")
#corpus_tfidf_mtx = corpus_tfidf.fit_transform(df['lemma_lower_text'])
#corpus_vocab = corpus_tfidf.get_feature_names()
corpus_vocab_file = 'nlp/corpus_vocab.pkl'
with open(corpus_vocab_file, 'rb') as f:
    corpus_vocab = pickle.load(f)


def candidate_job_score(job_id, user_profile_str):
    '''given user text input and job ID to which they
    applied, return cosine sim score for the pair'''
    job_idx = df.loc[df['_id'] == '8dcd846b-db99-547f-836c-bcda497cff0d'].index
    text = cleanup_text(user_profile_str)
    applicant_tfidf = TfidfVectorizer().fit(corpus_vocab)
    applicant_tfidf_vector = applicant_tfidf.transform([text])
    score = cosine_similarity(applicant_tfidf_vector, corpus_tfidf_mtx[job_idx]).flatten()
    return score


def train_profiler(train_documents):
    # TODO: Train profiler using TF-IDF
    print("Training profiler...")


def cleanup_text(text):
    '''Given a string, return it cleaned, tokenized, and lemmatized. '''
    # numbers, chars, etc.
    text = text.replace('_', ' ')
    text = text.replace('\r', ' ')
    text = text.replace('\n', ' ')
    text = text.replace('*', ' ')

    # digits, punctuation
    text = re.sub('\d+', ' ', text)

    # reduce extra spaces
    text = re.sub(' +', ' ', text)

    # get tokens, pos, etc.
    text = nlp(text)

    #lemmatize and remove punctuation, stopwords, etc.
    text = ' '.join([token.lemma_.lower() for token in text if not (token.is_stop) and not (token.is_punct)])
    
    return text



def find_job_matches(profile_description, top_n=5):
    # Lookup job matches using cosine similarity from our TF-IDF trained info
    assert type(profile_description) == str
    text = cleanup_text(profile_description)
    # TODO: MEL HERE
    applicant_tfidf = TfidfVectorizer().fit(corpus_vocab)

    # fit to new profile description
    applicant_tfidf_vector = applicant_tfidf.transform([text])
    cosine_similarities = cosine_similarity(applicant_tfidf_vector, corpus_tfidf_mtx).flatten()
    best_job_match_indices = cosine_similarities.argsort()[:-(top_n+1):-1]
    
    # Example: df['title'].iloc[best_indices]
    #return best_job_match_indices
    return df['_id'].iloc[best_job_match_indices]


def tests():
    """
    Test function, the following should pass to consider the analyzer correct.
    :return:
    """
    job_training = ['Software Engineer, Python, Java, Database, WebServer, API, json',

                    'Accountant, Experience with accounting software and data entry, '
                    'Experience with accounting and financial software, '
                    'Certified Public Accountant, CPA, '

                    'Certified Management Accountant',
                    ]

    # This Test list holds a pair of:
    # [<applicant profile>, <boolean>]
    # <applicant profile>: should have applicant profile description as String text
    # <boolean>: will indicate if the test should or should not have matches from the training dataset.
    job_applicants_test = [
        ['Python, NLP, data scientist, json', True],  # Should find matches
        ['Python, json, Java, Database, API, WebServer', True],  # Should find matches
        ['Manager, CPA, data Entry, programming, SQL', True],  # Should find matches
        ['CPA, Certified Management Accountant, financial software, accounting software', True],  # Should find match
        ['Experice creating tik tok, manage video team, video editing skills', False],  # Should NOT find match
    ]

    # start tests
    train_profiler(job_training)

    for applicant in job_applicants_test:
        matches = find_job_matches(applicant[0], top_n=5)
        if len(matches) > 0:
            print(matches)
        else:
            print('No Matches found!')


if __name__ == '__main__':
    tests()
