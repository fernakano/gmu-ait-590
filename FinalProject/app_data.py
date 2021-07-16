import json

# IMPORT JOB DATA
import pickle

jobs_file = open('career_builder_jobs_10501.json')
jobs = json.loads(jobs_file.read())

# SET BEHAVIORAL QUESTIONS
behavioral_questions = [
    {
        'id': 'job_conflict',
        'question': 'Have you faced any conflict with a different teammate? how did you resolve that?'
    },
]


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
