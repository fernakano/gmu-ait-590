"""
job_prescreener.py
Main application for the pre screener.
if we sent TEST as a parameter it runs the tests otherwise it runs the regular application

Job Database for training: https://data.world/opensnippets/us-job-listings-from-careerbuilder
"""
import re

from nltk import FreqDist

import job_sentiment as sent
import job_profiler as profiler
import app_data as data

jobs = data.Jobs()


def candidate_evaluation(candidate):
    """
    This function receives a candidate object and uses that to infer scores from attributes and
    append information back with the scored candidate.

    :param candidate:
    :return: scored candidate
    """
    print("Evaluating Candidate", candidate['name'])

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
    # Find Sentiment Score from Behavioral ansers
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
    # Find if tokenized list of Location provided has any match to provided ones in job description
    # TODO: use a geolocation library to improve score on distance.
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
    # Find Education Fit to identify if selected Education matches the required by the job.
    # TODO: create a hierarchical list to give more accurate score.. like HS < 2Yr. Degree < Bachelor < Master < PHD,
    #  so having the highers on the hierarchy could possibly cover lower titles.
    candidate['education_fit'] = 0
    if jobs.get_education_list_by_id(candidate['job_application_id']) in candidate['education']:
        candidate['education_fit'] = 1

    ################################################
    # Find candidate Experience fit
    ################################################
    # Find Experience Fit comparing years of experience vs required for the job.
    # Here we use Regex to identify experience requirement from Dataset.
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
    # Find candidate Profile fit
    ################################################
    # Find Profile Fit for the applicant versus the current job he is applying to.
    candidate['profile_fit'] = profiler.candidate_job_score(
        candidate['job_application_id'],
        candidate['job_profile'])[0]
    # candidate['profile_fit'] = (log(candidate['profile_fit']) + 1)
    candidate['profile_fit'] = candidate['profile_fit'] * 2

    ################################################
    #   CANDIDATE PRE_SCREENER APPROVAL
    #   (APPROVED, NOT_APPROVED, NEUTRAL)
    ################################################
    # Combine All scores here using weights to identify if applicant is good fit for current application.
    candidate['score'] = \
        min(min(candidate['profile_fit'], 0.4)
            + min((candidate['behavioral_sentiments_score'] / 2), 0.3)
            + min((candidate['experience_fit'] / 2) if exp_fit > 0 else -0.2, 0.2)
            + min(candidate['education_fit'], 0.05)
            + min(candidate['region_fit'], 0.05)
            , 1)

    # if a score is negative, we set as zero as a lower bound.
    candidate['score'] = 0 if candidate['score'] < 0 else candidate['score']

    # if candidate score is higher than 50% we consider a good fit on current setup
    # so HR Representative can pursue and verify if user is fit for interview.
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
    from datetime import datetime
    import uuid

    questions = data.Questions()

    test_candidates = [{
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
    }, {
        # user profile data
        'token': str(uuid.uuid4()),
        'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'name': 'Fernando Nakano',
        'first_name': 'Fernando',
        'last_name': 'Nakano',
        'email': 'fernakano@email.com',
        'education': 'Bachelor\'s Degree',
        'years_of_experience': '2',
        'location': 'Reston, VA, US',
        'phone': '1234567890',

        # Job related data
        'job_application_id': '8dcd846b-db99-547f-836c-bcda497cff0d',
        'job_profile': 'SQL, JSON, REST, XML, SOAP, NLP, Python, Java, Development, Software Architecture',
        'job_matches': [],
        'behavioral_questions': questions.get_behavioral_questions(),
        'behavioral_answers': [
            "i hate this",

            "this is a negative sentiment",

            "i have this"

            "this is a very bad feeling",
        ],
        'behavioral_sentiments': [],
        'score': 0
    }]

    test_results = [True, False]

    print("Start Testing for Candidate evaluation...")
    for i, candidate in enumerate(test_candidates):
        print()
        print("Candidate:", i)
        candidate = candidate_evaluation(candidate)
        print("profile_fit:", candidate['profile_fit'])
        print("behavioral_sentiments_score:", candidate['behavioral_sentiments_score'])
        print("region_fit:", candidate['region_fit'])
        print("education_fit:", candidate['education_fit'])
        print("experience_fit:", candidate['experience_fit'])
        print("score:", candidate['score'])
        print("pre_screener_approval:", candidate['pre_screener_approval'])

        if test_results[i] == candidate['pre_screener_approval']:
            print("Test Passed")


if __name__ == '__main__':
    tests()
