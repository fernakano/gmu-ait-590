# Job Pre Screener

## Documentation
### Features
    - Sentiment Analysis
    - Visualizations of the job screener
    - Summary report of deficit skills
    - Recommend Jobs that are better fit for the candidate.
    
#### Stretch goals
    - Skills matching
    - Years of experience
    - Ability to work with teams
    - Location
    - HTML form.
    - Pretty UI 

### Workflow
    1. Train application using job description dataset.
    2. User fills a form with job profile and behavioral questions.
    3. We look for jobs that match the user profile and the trained application dataset 
    using cosine similarity with the Vectorized documents.   
    4. We also pass the behavioral questions through a sentiment analysis to identify positiviness or negativiness 
    on user answers.
    5. Combine both job matches and sentiment analisys to identify if the user is a good fit for a Role.
    6. Display Summary Report of strenghts and defict skills
    7. Display Jobs recommendations that may be a better fit for the candidate
    8. Display visualizations of analisys on user data.



## Dependencies

## To Execute

