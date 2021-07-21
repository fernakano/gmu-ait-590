
import sys
import wikipedia
import re
import spacy
import en_core_web_sm

# load English tokenizer, tagger, parser, NER, and word vectors
nlp = en_core_web_sm.load()  # load here, takes a sec
verbose = False

def parse_sentence(text):
    doc = nlp(text)
    n_chunks = [chunk for chunk in doc.noun_chunks]
    
    subject = ''
    obj = ''
    verb_phrase = ''

    for chunk in n_chunks:    
        for token in chunk:
            if token.dep_ in ('pobj', 'dobj' ):
                obj = chunk
        for token in chunk:
            if token.dep_ in ('nsubj'):
                subject = chunk
    
    verbs = []
    for token in doc:
        if token.pos_ in ['VERB', 'AUX', 'ROOT']:
            verbs.append(str(token))
    
    verb_phrase = ' '.join([v for v in verbs])

    return subject, verb_phrase, obj


def parse_qstn(text, person_ents, verb_phrase):
    """ return who-question in answer form"""
    doc = nlp(text)
    ans_form = ''

    if person_ents is not None:
        ans_form = ' '.join([person_ents, verb_phrase])
        return ans_form

    # Determine if we're explaining a name or searching for a name:
    for token in doc:
        if token.text.lower() == 'who':
            pass
        elif token.pos_ == 'PUNCT':
            pass
        else:
            ans_form = ' '.join([ans_form, token.text])
    ans_form = ans_form + '.'
    ans_form = ans_form.replace('\n', '').replace('\r', '')
    return ans_form


def get_person_ents(text):
    doc = nlp(text)
    for ent in doc.ents:  
        # find entities that are people
        if ent.label_ == 'PERSON':
            who = text[ent.start_char : ent.end_char]
            return who


def name_provided(text):
    doc = nlp(text)
    name_provided = False
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            name_provided = True
    return name_provided

def search_wikipedia(text, obj):
    # TODO: handle case when provided name is in answer chunk:
    # Ex: Britney Spears is American singer Britney Spears

    titles = wikipedia.search(text)

    content = []
    summaries = []

    for t in titles:
        try:
            page = wikipedia.page(t)
            content.append(page.content)
            summaries.append(wikipedia.summary(t, sentences=1))
        except Exception as e:
            pass
            
    # narrow it down to the "who's"
    if name_provided(text):
        '''True (avoid name in answer) if we were given a name'''
        # we are searching for a title or other entity, not the name
        for c in content:
            doc = nlp(c)
            # Get keyword and matching chunks
            for ent in doc.ents:
                if ent.label_ not in ['DATE', 'PERSON', 'ORG', 'GPE']:
                    keyword = ent
                    for chunk in doc.noun_chunks:
                        if keyword.text in chunk.text:
                            ans = chunk.text
                            return ans

    # we are searching for a name
    else:
        for c in content:
            doc = nlp(c)
            for ent in doc.ents:
                if ent.label_ == 'PERSON':
                    #print(f'returning string of content person-ent: "{str(ent)}"')
                    return str(ent)
    
    return None


def answer_who(text):
    print(f'\n=== Input Text: {text} ===')
    
    subject, verb_phrase, obj = parse_sentence(text)
    if verbose:
        print(f'subject: {subject}\nverb_phrase: {verb_phrase}\nobj: {obj}')

    person_ents = get_person_ents(text)
    if verbose:
        print(f'person_ents: {person_ents}')

    ans_form = parse_qstn(text, person_ents, verb_phrase)
    if len(ans_form) >= len(text):
        if verbose:
            print(f'ans_form is too long: {len(ans_form)}')
        sys.exit(1)
    if verbose:
        print(f'ans_form: {ans_form}')

    w_ans = search_wikipedia(text, obj)
    if w_ans is not None:
        w_ans = w_ans.strip().rstrip()
    else:
        return "I am sorry, I don't know."
    if verbose:
        print(f"who from wikipedia:  {w_ans}")

    # Handle case when name is given (it's britney, b) 
    if name_provided(text):
        ans = ' '.join([ans_form, w_ans])

    else:
        '''we are looking up the name from wikipedia'''
        ans = ' '.join([w_ans, ans_form])

    if verbose:
        print("My Ans: ", ans)
    return(ans)


### TEST CASES ###
print(answer_who("Who is the current Queen of England?"))
#print(answer_who("Who was George Washington?"))
#print(answer_who("Who was Michael Jackson?"))
#print(answer_who("Who is Joe Biden?"))
print(answer_who("Who is the President of France?"))
#print(answer_who("is the president of France?"))
#print(answer_who("is the Principal at Washington-Liberty High School?"))
print(answer_who("Who designed Central Park?"))
print(answer_who("Who is Britney Spears?"))
print(answer_who("Who is Kamala Harris?"))
print(answer_who("Who is the Principal at Washington-Liberty High School?"))
print(answer_who("Who is the Sherrif of Arlington County?"))