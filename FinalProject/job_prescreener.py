"""
job_prescreener.py
Main application for the pre screener.

Job Database for training: https://data.world/opensnippets/us-job-listings-from-careerbuilder
"""

import sentiment as sent
import job_profiler as profiler


def main():
    print("Run Sentiment analizer tests")
    sent.tests()

    print("Run Job profiler tests")
    profiler.tests()


if __name__ == '__main__':
    main()
