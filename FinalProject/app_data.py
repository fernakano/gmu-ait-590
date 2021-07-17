import json
import pickle


################
#    Helper Database
################

# IMPORT JOB DATA
class Jobs:
    jobs = []

    def __init__(self):
        self.load_data()

    def load_data(self):
        # for reading also binary mode is important
        try:
            with open('career_builder_jobs_10501.json') as jobs_file:
                # jobs_file = open('career_builder_jobs_10501.json')
                print("Loading Job file List...")
                self.jobs = json.loads(jobs_file.read())
                print("Loading Job file List Complete...")
        except (OSError, IOError) as e:
            print("Job file does not exist, Can't upload job list...")

    def get_jobs(self):
        return self.jobs

    def get_top_n_jobs(self, top_n=10):
        return self.jobs[:top_n]

    def get_job_by_id(self, _id):
        for job in self.jobs:
            if job['_id'] == _id:
                return job

    def get_education_list(self):
        return list(set([job['education'] for job in self.jobs]))


# STORE HR DATA
class Applicants:
    applicants = {}

    def __init__(self):
        self.load_data()

    def load_data(self):
        # for reading also binary mode is important
        try:
            with open('applicants.db', 'rb') as db_file:
                self.applicants = pickle.load(db_file)
        except (OSError, IOError) as e:
            print("Applicant DB does not exist creating now...")
            with open('applicants.db', 'wb') as db_file:
                pickle.dump(self.applicants, db_file)

    def add_applicant(self, applicant):
        self.applicants[applicant['token']] = applicant
        with open('applicants.db', 'wb') as db_file:
            pickle.dump(self.applicants, db_file)

    def get_applicant_by_email(self, email):
        filtered_dict = {k: v for (k, v) in self.applicants.items() if email in v['email']}
        return filtered_dict

    def get_applicant_by_token(self, token):
        return self.applicants.get(token)

    def get_applicants_by_job_id(self, job_id):
        filtered_dict = {k: v for (k, v) in self.applicants.items() if job_id in v['job_application_id']}
        return filtered_dict

    def get_applicants(self):
        return self.applicants


# SET BEHAVIORAL QUESTIONS
class Questions:
    behavioral_questions = []

    def __init__(self):
        self.load_data()

    def load_data(self):
        print("Loading Behavioral Questions")
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
        ]

    def get_behavioral_questions(self):
        return self.behavioral_questions

    def get_behavioral_questions_by_id(self, _id):
        filtered_dict = [question for question in self.behavioral_questions if _id in question['id']]
        return filtered_dict
