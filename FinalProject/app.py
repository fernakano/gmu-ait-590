###############################################################################
# Final Term Team 3 Project - Job Prescreener                                 #
# AIT-590, Summer 2021                                                        #
# Group 3: Fernando, Melissa, Archer                                          #
# July 22, 2021                                                               #
#                                                                             #
# Assuming you have python 3                                                  #
# TO EXECUTE RUN:                                                             #
#  python app.py                                                              #
###############################################################################
#
# This is an application that HR professionals can use to screen and evaluate job
# candidates.  The tool is a flask-based application with a full web UI.  It accepts
# candidate application data and uses it to qualify the candidate against the job
# for which they applied.  The Job Prescreener evaluates the content of the user-
# provided data to evaluate their fitness for a position using multiple metrics including
# cosine similarity over entered text vs a pretrained TF-IDF model, geographical 
# data, experience, skills, and behavior analysis using sentiment analysis.  
# 
# This tool also provides value to the candidate by giving immediate feedback on their
# match to the job to which they apply, and also makes recommendations based on the
# match scores for other open positions within the database.  A company could use this to
# market optimal opportunities to interested or prospective new hires, even if they are
# not a perfect fit for the initial position.  
# 
# We use flask to serve a web application that cleans and processes input from users, and
# which stores the entries in a database for ongoing support to companies that use this system.
# The application benefits from tokenization, POS tags, regular expressions, tf-idf, text 
# edit distance metric calculation, and data transformation and manipulation.  
# 
# The interface is a RESTful web-based GUI.  We designed it this way so that it provides
# a clean and intuitive way for users to interact with the system.  The metrics and
# analysis can readily be customized to take into account whatever is important to the end
# users.  
"""
app.py
Main application for Job Application Pre Screener

This application is the Main Application to start the Web App.

This Application:
    - Run a WebApp built with Flask
    - Import job_prescrener.py to manage doing all the Job Application Screening tasks
    such as TF-IDF import and vectorization of the Job Application Documents, comparison between applicants Profile
     Job recommendation and Sentiment Analysis.
    - Import app_data.py for all Support helper data, such as Applicants, jobs and behavioral questions.
"""
from flask import Flask, render_template, request, redirect, Markup
import json
import uuid
import job_prescreener as ps
import app_data as data
from datetime import datetime

# Setup Flask App
app = Flask(__name__)

# Load Helper into app.
applicants = data.Applicants()
jobs = data.Jobs()
questions = data.Questions()


@app.route("/")
def home():
    """render template with job openings for the user"""
    return render_template('user_openings.html',
                           job_id=request.args.get("job_id"),
                           job_list=jobs.get_top_n_jobs(20))


@app.route("/user_form")
def user():
    """render template with job application form for the selected job id from openings
        If it is a USER it loads feedback and job recommendations
        If it is an HR Representative, it loads also candidate Fit information.
    """
    return render_template('user_form.html',
                           job_id=request.args.get("job_id"),
                           job_name=jobs.get_job_by_id(request.args.get("job_id"))['title'],
                           education_options=jobs.get_education_list(),
                           behavioral_questions=questions.get_behavioral_questions())


@app.route("/profiler", methods=["POST"])
def application():
    """Receives submited form from the user with job applications to perform the profiler
    on user profile information and behavioral questions"""

    # Read Behavioral question from app_data helper for use in Flask Template.
    behavioral_answers = []
    for question in questions.get_behavioral_questions():
        behavioral_answers.append(request.form[question['id']] if request.form[question['id']] else 0)

    candidate = {
        # user profile data
        'token': str(uuid.uuid4()),
        'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'name': str(" ".join([request.form['first_name'], request.form['last_name']])),
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'education': request.form.getlist('education'),
        'years_of_experience': request.form['experience'],
        'location': request.form['location'],
        'phone': request.form['phone'],

        # Job related data
        'job_application_id': request.form['job_application_id'],
        'job_profile': request.form['job_profile'],
        'job_matches': [],
        'behavioral_questions': questions.get_behavioral_questions(),
        'behavioral_answers': behavioral_answers,
        'behavioral_sentiments': [],
        'score': 0
    }

    print("Applicant: ", str(candidate['name']))
    print("Job Profile: ", str(candidate['job_profile']))

    # Here we will call the process for evaluating all the applicant data
    candidate = ps.candidate_evaluation(candidate)

    # Save Applicant to database after processing applicant data.
    applicants.add_applicant(candidate)

    return redirect('/report?' +
                    "&".join([
                        'token=' + candidate['token'],
                        'email=' + candidate['email']
                    ]))


@app.route("/report")
def report():
    """render template user report for Feedback on the Job application"""
    is_hr = True if request.args.get("hr") else False
    print(is_hr)
    candidate = applicants.get_applicant_by_token(request.args.get("token"))
    return render_template('user_report.html',
                           candidate=candidate,
                           skills_in_demand=json.dumps(candidate['skills_in_demand']),
                           candidate_fit=json.dumps(candidate['candidate_fit']),
                           is_hr=is_hr,
                           job=jobs.get_job_by_id(candidate['job_application_id']))


@app.route("/hr_openings")
def hr_openings():
    """render template with job openings for the HR Representative"""
    return render_template('hr_openings.html',
                           job_id=request.args.get("job_id"),
                           job_list=jobs.get_top_n_jobs(20))


@app.route("/hr_report")
def hr_report():
    """render template with applicants for an specific job for the HR Representative"""
    candidates = applicants.get_applicants_by_job_id(request.args.get("job_id"))
    return render_template('hr_report.html',
                           candidates=candidates,
                           job_name=jobs.get_job_by_id(request.args.get("job_id"))['title'])


# Run Flask App
app.run(debug=True)
