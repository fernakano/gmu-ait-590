"""
job_prescreener.py
Main application for the pre screener.
if we sent TEST as a parameter it runs the tests otherwise it runs the regular application

Job Database for training: https://data.world/opensnippets/us-job-listings-from-careerbuilder
"""
import sys
import re
from math import log

import nltk
import spacy
from nltk import FreqDist

import job_sentiment as sent
import job_profiler as profiler
import app_data as data

nltk.download('vader_lexicon')
jobs = data.Jobs()


def candidate_evaluation(candidate):
    # TODO: use sentiment anlysis and job profiler output to decide if candidate is a good fit
    #  or if there is a good position in the company for him.
    print("Evaluate Candidate")

    ################################################
    #   RUN JOB PROFILER TO FIND JOB MATCHES
    ################################################
    print("Run Job profiler")

    # Find the Job Matches for recommendation
    job_matches = profiler.find_job_matches(candidate['job_profile'])

    candidate['job_matches'] = [jobs.get_job_by_id(_id) for _id in job_matches]

    ################################################
    # Get List of Skills in demand from Job Matches
    ################################################
    # First Collect Tokenized Job skills
    tokenized_skills = []
    for job in candidate['job_matches']:
        tokenized_skills.extend(re.split(r'[.,]', job['skills']))

    # Find Frequency distribution of top 15 skills based on job matches
    freq_dist = FreqDist(tokenized_skills).most_common(15)

    # Convert to Dictionary for easy access on app
    candidate['skills_in_demand'] = {k: v for (k, v) in freq_dist}

    ################################################
    #   SENTIMENT ANALYSIS ON BEHAVIORAL QUESTIONS
    ################################################
    print("Run Sentiment analyzer")
    # sent.tests()
    sentiments = []
    sentiment_scores = []
    for question in candidate['behavioral_answers']:
        ss = sent.get_sentiment_score(question)
        sentiment_scores.append(1 if sent.is_sentiment_positive(ss) else 0)
        sentiments.append(sent.get_sentiment_as_string(ss))

    candidate['behavioral_sentiments'] = sentiments
    avg_bsc = sum(sentiment_scores) / len(sentiment_scores)
    candidate['behavioral_sentiments_score'] = avg_bsc if avg_bsc > 0 else 0

    ################################################
    # Find candidate region fit
    ################################################
    candidate['region_fit'] = 0
    job = jobs.get_job_by_id(candidate['job_application_id'])
    locations = candidate['location'].split(",")
    for location in locations:
        if location.strip() in [job['country'], job['locality'], job['region'], job['address'], job['postalCode']]:
            candidate['region_fit'] = 1
            break
    # if candidate['location'] in [job['country'], job['locality'], job['region'], job['address'], job['postalCode']]:
    #     candidate['region_fit'] = 1

    ################################################
    # Find candidate Education fit
    ################################################
    # Find Education Fit
    candidate['education_fit'] = 0
    if jobs.get_education_list_by_id(candidate['job_application_id']) in candidate['education']:
        candidate['education_fit'] = 1

    ################################################
    # Find candidate Experience fit
    ################################################
    # Find Experience Fit
    yoe = int(candidate['years_of_experience'])
    groups = re.match(r'(\d+).to.(\d+)', job['experience'])
    if groups:
        _min = int(groups.group(1))
        _max = int(groups.group(2))
        exp_fit = (yoe - _min) / (_max - _min)
    else:
        groups = re.match(r'At.least.(\d+)', job['experience'])
        if groups:
            _min = int(groups.group(1))
            _max = int(groups.group(1)) + 1
            exp_fit = (yoe - _min / 2) / (_max + 1 - _min)
        else:
            groups = re.match(r'Up.to.(\d+)', job['experience'])
            if groups:
                _min = 0
                _max = int(groups.group(1))
                exp_fit = (yoe - _min) / (_max - job['experience'])
            else:
                exp_fit = 1

    candidate['experience_fit'] = max(exp_fit, 0) if exp_fit < 0 else min(exp_fit, 1)

    ################################################
    # Find candidate Skills fit
    ################################################
    # Find Skills Fit
    candidate['profile_fit'] = profiler.candidate_job_score(
        candidate['job_application_id'],
        candidate['job_profile'])[0]
    # candidate['profile_fit'] = (log(candidate['profile_fit']) + 1)
    candidate['profile_fit'] = candidate['profile_fit'] * 2
    ################################################
    #   CANDIDATE PRE_SCREENER APPROVAL
    #   (APPROVED, NOT_APPROVED, NEUTRAL)
    ################################################
    print("Run PRE_SCREENER_APPROVAL")
    # Set here if applicant is good fit for current application.

    candidate['score'] = \
        min(min(candidate['profile_fit'], 0.4)
            + min((candidate['behavioral_sentiments_score'] / 2), 0.3)
            + min((candidate['experience_fit'] / 2) if exp_fit > 0 else -0.2, 0.2)
            + min(candidate['education_fit'], 0.05)
            + min(candidate['region_fit'], 0.05)
            , 1)

    candidate['score'] = 0 if candidate['score'] < 0 else candidate['score']

    candidate['pre_screener_approval'] = True if candidate['score'] > 0.5 else False

    ################################################
    # Build candidate Fit info for Radar Chart
    ################################################
    # Following order: ['Education', 'Region', 'Experience', 'Skills', 'Behavioral Score']
    candidate['candidate_fit'] = [candidate['education_fit'],
                                  candidate['region_fit'],
                                  candidate['experience_fit'],
                                  candidate['profile_fit'],
                                  candidate['behavioral_sentiments_score']]

    return candidate


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


if __name__ == '__main__':
    # if we sent TEST as a parameter it runs the tests
    if len(sys.argv) > 1:
        if sys.argv[1] == "TEST":
            tests()
    else:
        main()
