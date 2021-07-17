from flask import Flask, render_template, request, redirect, Markup
import json
import uuid
import job_prescreener as ps
import app_data as data
from datetime import datetime

app = Flask(__name__)

applicants = data.Applicants()
jobs = data.Jobs()
questions = data.Questions()


@app.route("/")
def home():
    return render_template('user_openings.html',
                           job_id=request.args.get("job_id"),
                           job_list=jobs.get_top_n_jobs(10))


@app.route("/user_form")
def user():
    return render_template('user_form.html',
                           job_id=request.args.get("job_id"),
                           job_name=jobs.get_job_by_id(request.args.get("job_id"))['title'],
                           education_options=jobs.get_education_list(),
                           behavioral_questions=questions.get_behavioral_questions())


@app.route("/profiler", methods=["POST"])
def application():
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
        'phone': request.form['phone'],
        'years_of_experience': request.form['experience'],
        'location': request.form['location'],

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

    # Here we will call the process for all the applicant data
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
    candidate = applicants.get_applicant_by_token(request.args.get("token"))
    return render_template('user_report.html',
                           candidate=candidate,
                           skills_in_demand=json.dumps(candidate['skills_in_demand']),
                           candidate_fit=json.dumps(candidate['candidate_fit']))


@app.route("/hr_openings")
def hr_openings():
    return render_template('hr_openings.html',
                           job_id=request.args.get("job_id"),
                           job_list=jobs.get_top_n_jobs(10))


@app.route("/hr_report")
def hr_report():
    candidates = applicants.get_applicants_by_job_id(request.args.get("job_id"))
    return render_template('hr_report.html',
                           candidates=candidates,
                           job_name=jobs.get_job_by_id(request.args.get("job_id"))['title'])


app.run(debug=True)
