# Job Pre Screener

## Documentation

    Here we will document the features required for the Job Pre Screener.

### Features

    - Behavioral Score (Sentiment Analysis)
    - Years of experience score (Regex Match)
    - Location Score (String Match)
    - Education Score (String Match)
    - Profile Score (TF-IDF + Cosine Similarity)
    - Summary report of deficit skills
    - Chart Visualizations of the job screener
    - Recommend Jobs that are better fit for the candidate.
    - HTML form.
    - Usable decent visualt for the alpha version of the UI


### Workflow

    1. Train application using job description dataset.
    2. User fills a form with job profile and behavioral questions.
    3. We look for jobs that match the user profile and the trained application dataset 
    using cosine similarity with the Vectorized documents.   
    4. We also pass the behavioral questions through a sentiment analysis to identify positiviness or negativiness 
    on user answers.
    5. Identify Location, Years of Experience and Education scores.
    6. Combine job matches, sentiment analisys and other scores 
        to identify if the user is a good fit for a Role using a weighted formula as follows:
   
   ```python 
   candidate['score'] = \
        min(min(candidate['profile_fit'], 0.4)
            + min((candidate['behavioral_sentiments_score'] / 2), 0.3)
            + min((candidate['experience_fit'] / 2) if exp_fit > 0 else -0.2, 0.2)
            + min(candidate['education_fit'], 0.05)
            + min(candidate['region_fit'], 0.05)
            , 1)
   ``` 
    
    7. Display Summary Report of strenghts and defict skills
    8. Display Jobs recommendations that may be a better fit for the candidate
    9. Display visualizations of analisys on user data.

## Dependencies
    - We developed this application using Python3.

    - pip install numpy
    - pip install pandas
    - pip install nltk
    - pip install scikit-learn
    - pip install flask
    - pip install spacy
    - python -m spacy download en_core_web_sm

## To Execute
    - Go to the FinalProject/ folder to start running the scripts. 

### To generate our TF-IDF Matrix
    We need to execute the complete Notebook AIT590-Project-Job-Data-Final-Summary-Notebook.ipynb
    
    Note: The Notebook is already executed and we saved outputs on the nlp folder to save time
    since the execution time can take 20+ minutes for this dataset depending on the computer.

### Main App:

    RUN our application, please execute: python app.py
    (make sure it is using python3 and all the other dependencies are installed)

    This will serve a Web app on http://localhost:5000 or http://127.0.0.1:5000 
    that can be accessed through your browser.

    (localhost or 127.0.0.1 can vary from computer to compueter depending on local configurations)
    
    This Webserver will have some pages to test the application as shown bellow:

#### On the Applicant side

    - http://127.0.0.1:5000/
        This will open the main job list for the Applicants
        then once you select a job listingit should send you to the following page:
    
    - http://127.0.0.1:5000/user_form
        On the User form, The applicant will fill the form with their information as well as their job profile,
        once they click submit, the form passes through the /profiler endpoint 
        and then land on the following reprt page:
    
    - http://127.0.0.1:5000/report
        On this page the user can see their instant feedback about the application and job recommendations
        related to their profile.

#### On the HR Representative Side

    - http://127.0.0.1:5000/hr_openings
        You can see all the Job lists as an HR Representative,
    and if you select a job opening, you get sent to the HR report page:
    
    -http://127.0.0.1:5000//hr_report 
        Here it will will show the list of applicants for that specific opening with their respective score
    to make it easier to identify the applicants that have a good score or bad scores we will color code as follows: 
        . >0.5 will color coded as Green
        . <0.5 will color coded as Red
    If the HR Representative selects one of the Applicants they will be redirected to the user report page
    with extra details about why the user may or may not be a good fit.
    
    - http://127.0.0.1:5000/report?hr=True
        This will show more detailed analisys on the user and describe why the user Fit received the respective score, 
    to help on decision making if the user should proceed with interviews or not.


### Test Helpers
    It is not required but also possible to test most files independently as well with test functions 
    that were created to support development.
    
    You just need to run Files independently directly.

    -   Job Pre Screener module tests:
            This will do most business logic and glue together executions of job profiler and sentiment analysis
        python3 job_prescreener.py
    
    -   Job Profiler module tests:
            This will do retrieve simillar jobs to the input user jobs from our job description trained database 
        python3 job_profiler.py

    -   Sentiment Analysis module tests:
            This will run sentiment anlisys on phrases and return Positive or Negative.
        python3 job_sentiment.py
