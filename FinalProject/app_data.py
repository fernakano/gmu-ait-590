"""
app_data.py
Helper function to manage Persistent data.

This file contain Classes to help manage data for:
    - Jobs
    - Applicants
    - Behavioral Questions
    - Profiler Preprocessed Data

it has functions to retrieve data and perform data filters too.
"""

import json
import pickle
import pandas as pd


################
#    Helper Database
################

# IMPORT JOB DATA
class Jobs:
    jobs = []

    # Initialize the class loading the data if it exists.
    def __init__(self):
        self.load_data()

    def load_data(self):
        """Load the data if it exists."""
        try:
            with open('career_builder_jobs_10501.json') as jobs_file:
                # jobs_file = open('career_builder_jobs_10501.json')
                print("Loading Job file List...")
                self.jobs = json.loads(jobs_file.read())
        except (OSError, IOError) as e:
            print("Job file does not exist, Can't upload job list...")

    def get_jobs(self):
        """Return List of ALl jobs"""
        return self.jobs

    def get_top_n_jobs(self, top_n=10):
        """Return List of TOP N jobs"""
        return self.jobs[:top_n]

    def get_job_by_id(self, _id):
        """Return job based on job_id"""
        for job in self.jobs:
            if job['_id'] == _id:
                return job

    def get_experience_list(self):
        """Return List of unique education items in job"""
        return sorted(list(set([job['experience'] for job in self.jobs if job['experience'] not in ""])))

    def get_education_list(self):
        """Return List of unique education items in job"""
        return sorted(list(set([job['education'] for job in self.jobs if job['education'] not in ""])))

    def get_education_list_by_id(self, _id):
        """Return List of education for selected job"""
        for job in self.jobs:
            if job['_id'] == _id:
                return job['education']


# STORE HR DATA
class Applicants:
    applicants = {}

    # Initialize the class loading the data if it exists.
    def __init__(self):
        print("Loading Applicant Data")
        self.load_data()

    def load_data(self):
        """Load the data if it exists. uses binary to store as a dictionary"""
        try:
            with open('applicants.db', 'rb') as db_file:
                self.applicants = pickle.load(db_file)
        except (OSError, IOError) as e:
            print("Applicant DB does not exist creating now...")
            with open('applicants.db', 'wb') as db_file:
                pickle.dump(self.applicants, db_file)

    def add_applicant(self, applicant):
        """Add applicants to the database and update the file"""
        self.applicants[applicant['token']] = applicant
        with open('applicants.db', 'wb') as db_file:
            pickle.dump(self.applicants, db_file)

    def get_applicant_by_email(self, email):
        """Return Applicant filtered by email"""
        filtered_dict = {k: v for (k, v) in self.applicants.items() if email in v['email']}
        return filtered_dict

    def get_applicant_by_token(self, token):
        """Return Applicant filtered by application token"""
        return self.applicants.get(token)

    def get_applicants_by_job_id(self, job_id):
        """Return List of Applicants filtered by application job_id"""
        filtered_dict = {k: v for (k, v) in self.applicants.items() if job_id in v['job_application_id']}
        return filtered_dict

    def get_applicants(self):
        """Return List of All Applicants"""
        return self.applicants


# SET BEHAVIORAL QUESTIONS
class Questions:
    behavioral_questions = []

    # Initialize the class loading the data if it exists.
    def __init__(self):
        print("Loading Behavioral Questions")
        self.load_data()

    def load_data(self):
        """Load the data as a list of behavioral questions"""
        self.behavioral_questions = [
            {
                'id': 'job_conflict',
                'question': 'Have you faced any conflict with a different teammate? how did you resolve that?'
            },
            {
                'id': 'job_experience',
                'question': 'What are some of the projects you have worked? tell me a bit about your experience.'
            },
            {
                'id': 'job_proud',
                'question': 'What are you most proud about in your career so far?'
            },
            {
                'id': 'job_here',
                'question': 'Why do you want to work here?'
            },

        ]

    def get_behavioral_questions(self):
        """Load the data as a list of behavioral questions"""
        return self.behavioral_questions

    def get_behavioral_questions_by_id(self, _id):
        filtered_dict = [question for question in self.behavioral_questions if _id in question['id']]
        return filtered_dict


class ProfilerData:
    df = None
    corpus_tfidf_mtx = {}
    corpus_vocab = {}

    # Initialize the class loading the data if it exists.
    def __init__(self):
        print("Loading Saved Profiler Data")
        self.load_data()

    def load_data(self):
        """Load the stored profiler data for application startup performance"""
        try:
            self.df = pd.read_csv('nlp/carry_on_df.csv')
        except (OSError, IOError) as e:
            print("Carry Of DF file does not exist")

        try:
            corpus_tfidf_mtx_file = 'nlp/our_tfidf_mtx_8.pkl'
            with open(corpus_tfidf_mtx_file, 'rb') as f:
                self.corpus_tfidf_mtx = pickle.load(f)
        except (OSError, IOError) as e:
            print("Corpus TF-IDF Matrix file does not exist")

        try:
            corpus_vocab_file = 'nlp/corpus_vocab.pkl'
            with open(corpus_vocab_file, 'rb') as f:
                self.corpus_vocab = pickle.load(f)
        except (OSError, IOError) as e:
            print("Corpus Vocab file does not exist")

    def get_carry_of_df(self):
        return self.df

    def get_corpus_tfidf_mtx(self):
        return self.corpus_tfidf_mtx

    def get_corpus_vocab(self):
        return self.corpus_vocab
