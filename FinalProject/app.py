from flask import Flask, render_template, request, redirect
import json
import uuid
import job_prescreener as ps
from datetime import datetime

app = Flask(__name__)


@app.route("/")
def home():
    return render_template('user_form.html')


@app.route("/profiler", methods=["POST"])
def application():
    candidate = {
        'token': str(uuid.uuid4()),
        'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'name': str(" ".join([request.form['first_name'], request.form['last_name']])),
        'profile': request.form['job_profile'],
        'behavioral_questions': [request.form['job_conflict']]
    }

    print("Applicant: ", str(candidate['name']))
    print("Job Profile: ", str(candidate['profile']))
    print("Job Conflict: ", str(candidate['behavioral_questions'][0]))

    candidate = ps.candidate_evaluation(candidate)

    return redirect('/report?' +
                    "&".join([
                        'token=' + candidate['token'],
                        'candidate=' + json.dumps(candidate)
                    ]))


@app.route("/report")
def report():
    return render_template('report.html')


app.run(debug=True)
