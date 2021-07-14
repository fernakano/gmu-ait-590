from flask import Flask, render_template, request, redirect, Markup
import json
import uuid
import job_prescreener as ps
from datetime import datetime

app = Flask(__name__)

behavioral_questions = [
    {
        'id': 'job_conflict',
        'question': 'Have you faced any conflict with a different teammate? how did you resolve that?'
    }
]


@app.route("/")
def home():
    return render_template('user_form.html', behavioral_questions=behavioral_questions)


@app.route("/profiler", methods=["POST"])
def application():
    behavioral_answers = []
    for question in behavioral_questions:
        behavioral_answers.append(request.form[question['id']])

    candidate = {
        'token': str(uuid.uuid4()),
        'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'name': str(" ".join([request.form['first_name'], request.form['last_name']])),
        'job_profile': request.form['job_profile'],
        'job_matches': [],
        'behavioral_questions': behavioral_questions,
        'behavioral_answers': behavioral_answers,
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
