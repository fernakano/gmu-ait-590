from flask import Flask, render_template, request, redirect
import json
import job_prescreener as ps

app = Flask(__name__)


@app.route("/")
def home():
    return render_template('user_form.html')


@app.route("/application", methods=["POST"])
def application():
    candidate = {
        'name': str(" ".join([request.form['first_name'], request.form['last_name']])),
        'profile': request.form['job_profile'],
        'behavioral_questions': [request.form['job_conflict']]
    }

    print("Applicant: ", str(candidate['name']))
    print("Job Profile: ", str(candidate['profile']))
    print("Job Conflict: ", str(candidate['behavioral_questions'][0]))

    candidate = ps.candidate_evaluation(candidate)

    return redirect('/report?token=abcd1234&candidate='+json.dumps(candidate))


@app.route("/report")
def report():
    return render_template('report.html')


app.run(debug=True)
