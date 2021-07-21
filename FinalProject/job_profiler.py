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

import app_data

# load English tokenizer, tagger, parser, NER and word vectors
nlp = en_core_web_sm.load()
data = app_data.ProfilerData()

# We created this subset dataframe in a notebook and load it here for speed
df = data.get_carry_of_df()

# We created this matrix in a notebook and load it here for speed
corpus_tfidf_mtx = data.get_corpus_tfidf_mtx()

# We created the vocabulary list in a notebook and load it here for speed
corpus_vocab = data.get_corpus_vocab()


def candidate_job_score(job_id, user_profile_str):
    '''given user text input and job ID to which they
    applied, return cosine sim score for the pair'''
    job_idx = df.loc[df['_id'] == job_id].index
    text = cleanup_text(user_profile_str)
    applicant_tfidf = TfidfVectorizer().fit(corpus_vocab)
    applicant_tfidf_vector = applicant_tfidf.transform([text])
    score = cosine_similarity(applicant_tfidf_vector, corpus_tfidf_mtx[job_idx]).flatten()
    return score


def train_profiler(train_documents):
    # we are loading a pretrained profiler at initialization
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

    # lemmatize and remove punctuation, stopwords, etc.
    text = ' '.join([token.lemma_.lower() for token in text if not (token.is_stop) and not (token.is_punct)])

    return text


def find_job_matches(profile_description, top_n=5):
    """ Lookup job matches using cosine similarity from our TF-IDF trained matrix """
    assert type(profile_description) == str
    text = cleanup_text(profile_description)
    applicant_tfidf = TfidfVectorizer().fit(corpus_vocab)

    # Fit input profile to new profile description
    applicant_tfidf_vector = applicant_tfidf.transform([text])

    # Find Cosine Similarity to profile
    cosine_similarities = cosine_similarity(applicant_tfidf_vector, corpus_tfidf_mtx).flatten()
    best_job_match_indices = cosine_similarities.argsort()[:-(top_n + 1):-1]

    return df['_id'].iloc[best_job_match_indices]


def tests():
    """
    Test function, the following should pass to consider the analyzer correct.
    :return:
    """
    import app_data as data
    from datetime import datetime
    import uuid

    questions = data.Questions()
    jobs = data.Jobs()

    candidates = [{
        # user profile data
        'token': str(uuid.uuid4()),
        'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'name': 'Fernando Nakano',
        'first_name': 'Fernando',
        'last_name': 'Nakano',
        'email': 'fernakano@email.com',
        'education': 'Bachelor\'s Degree',
        'years_of_experience': '15',
        'location': 'Reston, VA, US',
        'phone': '1234567890',

        # Job related data
        'job_application_id': '8dcd846b-db99-547f-836c-bcda497cff0d',
        'job_profile': 'SQL, JSON, REST, XML, SOAP, NLP, Python, Java, Development, Software Architecture',
        'job_matches': [],
        'behavioral_questions': questions.get_behavioral_questions(),
        'behavioral_answers': [
            "There was a teammate that never liked anyone's idea, so to deal with that i talked to him to understand "
            "what was the problem. It turns out he had a personal problem at home, so things were great after that "
            "and he was glad that i reached out to him to help!",

            "There was a teammate that never liked anyone's idea, so to deal with that, i called in for a meeting "
            "and told him he was a really bad work team mate and i didn't want to work with him anymore.",

            "There was a teammate that never liked anyone's idea, so to deal with that, i called HR to complain "
            "about his behaviour"

            "There was a teammate that never liked anyone's idea, so i offered some tips to improve his relationship "
            "with other teammates and he thanked me for helping him!",
        ],
        'behavioral_sentiments': [],
        'score': 0
    }]

    print(".....Testing candidates Profiling start.....")
    for candidate in candidates:
        print()
        print("Finding score for: " + candidate['name'])
        score = candidate_job_score('8dcd846b-db99-547f-836c-bcda497cff0d', candidate['job_profile'])
        print('Score:', score[0])

        print('Finding Job Recommendations')
        matches = find_job_matches(candidate['job_profile'], top_n=5)
        if len(matches) > 0:
            job_matches = [jobs.get_job_by_id(_id) for _id in matches]
            for job in job_matches:
                print(job['_id'], job['title'])
        else:
            print('No Job Matches found!')

    print(".....Testing candidates Profiling end.....")


if __name__ == '__main__':
    tests()
