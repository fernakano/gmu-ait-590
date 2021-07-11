"""
job_prescreener.py
Main application for the pre screener.

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
