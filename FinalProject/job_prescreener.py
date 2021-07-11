"""
job_prescreener.py
Main application for the pre screener.

Job Database for training: https://data.world/opensnippets/us-job-listings-from-careerbuilder
"""
import sys

import sentiment as sent
import job_profiler as profiler


def candidate_evaluation(candidate):
    # TODO: use sentiment anlysis and job profiler output to decide if candidate is a good fit
    #  or if there is a good position in the company for him.
    print("Evaluate Candidate")

    print("Run Sentiment analyzer tests")
    # sent.tests()
    sentments = []
    for question in candidate['behavioral_questions']:
        ss = sent.get_sentiment_score(question)
        sentments.append(sent.get_sentiment_as_string(ss))

    print(sentments)
    # print("Run Job profiler tests")
    # profiler.tests()


def tests():
    print("Testing Candidates")
    test_candidates = [
        {
            'name': 'Jane Doe',
            'profile': 'Software Engineer, Experience with Python, Java and Databases',
            'behavioral_questions': [
                "There was a teammate that never liked anyone's idea, so to deal with that, "
                "i called HR to complain about his behaviour"]
        },
        {
            'name': 'John Doe',
            'profile': 'Accountant, CPA, Certified Management Accountant',
            'behavioral_questions': [
                "There was a teammate that never liked anyone's idea, "
                "so i offered some tips to improve his relationship with other "
                "teammates and he thanked me for helping him!"]
        },
    ]

    for candidate in test_candidates:
        print(candidate['name'])
        candidate_evaluation(candidate)


def main():
    # TODO: Add question and answer form/bot here.
    print("Are you looking for a job? you came to the right place!")
    candidate_evaluation()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "TEST":
            tests()
    else:
        main()
