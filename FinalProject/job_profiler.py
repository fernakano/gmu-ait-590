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


# TODO: read json as Data Frame.
# df = pd.read_json('career_builder_jobs_10501.json')
# print(df.to_string())

def train_profiler(train_documents):
    # TODO: Train profiler using TF-IDF
    print("Training profiler...")


def find_job_matches(profile_description, top_n=5):
    # TODO: Lookup job matches using cosine similarity from our TF-IDF trained info
    return []


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
