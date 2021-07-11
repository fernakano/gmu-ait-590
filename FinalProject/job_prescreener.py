"""
job_prescreener.py
Main application for the pre screener.

Job Database for training: https://data.world/opensnippets/us-job-listings-from-careerbuilder
"""

import sentiment as sent
import job_profiler as profiler


def candidate_evaluation():
    # TODO: use sentiment anlysis and job profiler output to decide if candidate is a good fit
    #  or if there is a good position in the company for him.
    print("Evaluate Candidate")

    print("Run Sentiment analyzer tests")
    sent.tests()

    print("Run Job profiler tests")
    profiler.tests()


def main():
    # TODO: Add question and answer form/bot here.
    print("Are you looking for a job? you came to the right place!")
    candidate_evaluation()


if __name__ == '__main__':
    main()
