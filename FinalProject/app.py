from flask import Flask, render_template, request, redirect, Markup
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
        'job_profile': request.form['job_profile'],
        'job_matches': [],
        'behavioral_questions': [request.form['job_conflict']],
        'behavioral_sentiments': []
    }

    print("Applicant: ", str(candidate['name']))
    print("Job Profile: ", str(candidate['job_profile']))
    print("Job Conflict: ", str(candidate['behavioral_questions'][0]))

    candidate = ps.candidate_evaluation(candidate)

    # test sample
    candidate['job_matches'] = ['sample job 1', 'sample job 2']

    return redirect('/report?' +
                    "&".join([
                        'token=' + candidate['token'],
                        'candidate=' + json.dumps(candidate)
                    ]))


@app.route("/report")
def report():
    candidate = json.loads(Markup(request.args.get("candidate")))
    return render_template('report.html', candidate=candidate)


app.run(debug=True)
