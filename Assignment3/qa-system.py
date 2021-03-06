#######################################
#           ASSIGNMENT 3              #
# AIT-590, Summer 2021                #
# Group 3: Fernando, Melissa, Archer  #
# July 7, 2021                        #
#                                     #
# Assuming you have python 3          #
# TO EXECUTE RUN:                     #
#  python qa-system.py                #
#######################################
"""
DESCRIPTION: 

qa-system.py uses pattern matching and intelligent parsing to answer
user-provided questions of who/where/what/when in an interactive
environment.  Questions are parsed for which w-word, and are processed
individually depending on entities identified, nouns, and POS positions.

BONUS FUNCTIONALITY:  

Use SpaCy's NER to perform advanced
entity recognition to assist with improved question understanding
and accuracy of answers!

Example Output:

(ml-env) melissas-mbp:Assignment3 melissacirtain$ python qa-system.py 
hello!

    This is a QA system by AIT590 Group 3.  It will try to answer
    your questions that start with Who, What, When, or Where.  Enter "exit"
    to leave the program.

=?> what is a garden?
=>  A garden is a planned space, usually outdoors, set aside for the display, cultivation, or enjoyment of plants and other forms of nature, as an ideal setting for social or solitary human life.

=?> who is George Washington?
=>  George Washington (February 22, 1732 – December 14, 1799) was an American political leader, military general, statesman, and Founding Father of the United States, who served as the first president of the United States from 1789 to 1797.

=?> Why do we exist?
=>  I am sorry, I can only answer questions starting with Who, What, When or Where.

=?> exit

Thank you!  Goodbye.

"""

# for teting: try running with these questions:
# who is the National Park Service and is it part of the USA? Is Melissa available?
# what is the date?
# =?> who wrote God Bless the USA?

import sys
import wikipedia
import re
import spacy
import en_core_web_sm

# load English tokenizer, tagger, parser, NER, and word vectors
nlp = en_core_web_sm.load()  # load here, takes a sec
verbose = False

if len(sys.argv) != 2:
    outfile = 'mylogfile.txt'
else:
    outfile = sys.argv[1]

def make_introduction():
    '''start the conversation with instructions, get initial question'''

    intro = '''
    This is a QA system by AIT590 Group 3.  It will try to answer
    your questions that start with Who, What, When, or Where.  Enter "exit"
    to leave the program.\n\n=?> '''
    qstn = input(intro)
    return qstn


def qstn_is_valid(qstn):
    '''Return True if qstn begins with who, what, when, or where'''
    if re.match(r"^([W|w]hen|[W|w]here|[W|w]ho|[W|w]hat)\b", qstn.lower()):
        return True
    else:
        return False


def get_nes(qstn):
    '''return a list of Named Entities or an empty list if none found'''

    # named entities list
    nes = []

    # use SpaCy to identify NEs
    mytext = nlp(qstn)

    for entity in mytext.ents:
        nes.append(entity)
        # print(f'entity: {entity}, ({entity.label_})')

    if nes == []:
        # print(f'no named entities found for {qstn}')
        pass

    return nes


def query_wiki(qstn, nes):
    '''query our data sources online, return text result'''

    long_answer = ''
    summaries = []

    # wikipedia/google queries
    for ne in nes:
        # print(f'querying on ne {ne.text}')
        titles = wikipedia.search(ne.text)
        for t in titles:
            try:
                page = wikipedia.page(t)
                # summaries.append(wikipedia.summary(t, sentences=1))
                summaries.append(wikipedia.page(t).content
                                 .replace('\n', '. '))  # This is to improve sentence break from spacy.
            except Exception as e:
                pass

        # print(f'Summaries:')
        # for s in summaries:
        #    print(s[0:50])

    if summaries == []:
        # try the nouns if no results with entity search
        mytext = nlp(qstn)
        nouns = [x for x in mytext if x.pos_ == 'NOUN']
        # print('Found Nouns:')
        # print(nouns)
        for n in nouns:
            titles = wikipedia.search(n.text)
            try:
                for t in titles:
                    try:
                        summaries.append(
                            wikipedia.summary(title=t, sentences=200, auto_suggest=False, redirect=True)
                                .replace('\n', '. '))
                    # To resolve Disambiguation errors
                    except wikipedia.DisambiguationError as e:
                        for option in e.options:
                            if nlp(option.lower()).similarity(nlp(str(n).lower())) > 0.9:
                                summaries.append(wikipedia.WikipediaPage(t).content
                                                 .replace('\n', '. '))  # help identify sentences on explicit break line
                                continue
                    # summaries.append(wikipedia.summary(n.text, sentences=1))
                    # summaries.append(wikipedia.page(t).content)
            except Exception as e:
                print(f'in noun try, failed: {e}')

    return summaries


def get_verbs_from_nlp_doc(qstn_nlp):
    verbs = []
    for word in qstn_nlp.doc:
        if word.pos_ == "VERB":
            verbs.append(word)
    return verbs


def get_nouns_from_nlp_doc(qstn_nlp):
    nouns = []
    for word in qstn_nlp:
        if word.pos_ == "NOUN":
            nouns.append(word)
    return nouns


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


def get_person_ents(text):
    doc = nlp(text)
    for ent in doc.ents:  
        # find entities that are people
        if ent.label_ == 'PERSON':
            who = text[ent.start_char : ent.end_char]
            return who


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
    ''' handle questions beginning with "who" '''

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
    return (ans)


def answer_what(qstn, nes, long_answer):
    ''' handle questions beginning with "what" '''
    qstn_nlp = nlp(qstn)

    verbs = get_verbs_from_nlp_doc(qstn_nlp)

    if not nes:
        nes.extend(get_nouns_from_nlp_doc(qstn_nlp))

    possible_answers = []
    for lanswer in long_answer:
        for sent in nlp(lanswer).doc.sents:
            for ne in nes:
                if ne.text.lower() in sent.text.lower():
                    possible_answers.append(sent.text)

    if len(possible_answers) > 0:
        for possible_answer in possible_answers:
            if len(verbs) > 0:
                for verb in verbs:
                    if str(verb) in possible_answer:
                        return possible_answer
            else:
                return possible_answers[0]

    # TODO: formulate a number of "what" questions/answers around the NEs
    # 1. what is the|a XYZ: XYZ is ABC (maybe first summary?)
    # ...

    return ""


def answer_when(qstn, nes, long_answer):
    ''' handle questions beginning with "when" '''
    qstn_nlp = nlp(qstn)

    verbs = get_verbs_from_nlp_doc(qstn_nlp)

    if not nes:
        nes.extend(get_nouns_from_nlp_doc(qstn_nlp))

    possible_answers = []
    for lanswer in long_answer:
        for sent in nlp(lanswer).doc.sents:
            for ne in nes:
                if ne.text.lower() in sent.text.lower():
                    possible_answers.append(sent.text)

    try:
        if len(possible_answers) > 0:
            for possible_answer in possible_answers:
                p_answer_nlp = nlp(possible_answer)
                for ent in p_answer_nlp.ents:
                    if ent.label_ == "DATE":
                        if len(verbs) > 0:
                            for verb in verbs:
                                if str(verb) in possible_answer:
                                    for text in p_answer_nlp.doc:
                                        if str(verb.lemma_) == text.lemma_ and nes:
                                            if nes[0].text not in str(p_answer_nlp.doc[:ent.end]):
                                                return nes[0].text + " " + str(text) + " " + str(
                                                    p_answer_nlp.doc[:ent.end])
                                            else:
                                                return p_answer_nlp.doc[:ent.end]
                        else:
                            return p_answer_nlp.doc[:ent.end]

        else:
            return possible_answers[0]
    except Exception as e:
        # print(f'i dont understand {e}')
        pass

    # TODO: formulate a number of "when" questions/answers around the NEs
    # 1. when is XYZ: XYZ is at|on|after|during|in ABC
    # ...

    return ""


def answer_where(qstn, nes, long_answer):
    ''' handle questions beginning with "where" '''
    qstn_nlp = nlp(qstn)

    if not nes:
        nes.extend(get_nouns_from_nlp_doc(qstn_nlp))

    verbs = get_verbs_from_nlp_doc(qstn_nlp)

    prep = "is located"
    location, possible_answers = [], []
    for lanswer in long_answer:
        for sent in nlp(lanswer).doc.sents:
            for verb in verbs:
                if str(verb.lemma_) in sent.lemma_.lower():
                    prep = str(verb)
            for ne in nes:
                if ne.text.lower() in sent.text.lower():
                    for ent in sent.ents:
                        if ent.label_ in ["GPE"] and len(sent.conjuncts) == 0:
                            location.append(ent.text)
                    if len(location) > 0:
                        possible_answers.append(ne.text + " " + prep + " in " + ", ".join(set(location)))

    if len(possible_answers) > 0:
        for possible_answerr in possible_answers:
            if len(verbs) > 0:
                for verb in verbs:
                    if str(verb) in possible_answerr:
                        return possible_answerr
            else:
                return possible_answers[0]
    # TODO: formulate a number of "where" questions/answers around the NEs
    # 1. where is the XYZ: XYZ is in|at|on (the)+ ABC
    # ...

    return ""


def send_qstn_to_switchboard(qstn):
    '''use online resources to try to answer question.'''

    # get Named Entitiess from spacy
    nes = get_nes(qstn)

    # query for data with named entities (or nouns if no NEs)
    long_answer = query_wiki(qstn, nes)

    # handle no results
    if long_answer == []:
        # we have no results to parse, return idk
        return "I'm sorry, I do not know the answer."

    # get the first word
    w_word = re.match(r"^([\w\-]+)", qstn.lower())

    # default answer
    default_ans = "I am sorry, I don't know the answer."

    # answer depending on first word (who/what/where/when)
    if w_word.group().lower() == 'who':
        # handle 'who' type questions
        ans = answer_who(qstn)

    elif w_word.group().lower() == 'what':
        # handle 'what' type questions
        ans = answer_what(qstn, nes, long_answer)

    elif w_word.group().lower() == 'where':
        # handle 'where' type questions
        ans = answer_where(qstn, nes, long_answer)

    elif w_word.group().lower() == 'when':
        # handle 'when' type questions
        ans = answer_when(qstn, nes, long_answer)

    else:
        # ERROR - case not handled
        print('ERROR--should not get here...')
        assert False

    final_ans = str(ans) if str(ans) != "" else default_ans

    with open(outfile, 'a') as f:
        f.write(f'=?> {qstn}\n')
        f.write(f'=>  {final_ans}\n\n')
    #return str(ans) if str(ans) != "" else default_ans
    return final_ans


def process_questions(qstn):
    ''' validate questions, request answers, prompt for next question'''

    # validate question begins with who, what, when, or where

    if qstn_is_valid(qstn):
        # question is valid; try to find an answer
        ans = send_qstn_to_switchboard(qstn)

    else:
        ans = 'I am sorry, I can only answer questions starting with '
        ans += 'Who, What, When or Where.'

    # respond and get next question
    qstn = input(f'=>  {ans}\n\n=?> ')

    return qstn


def main():
    print('hello!')

    # introduction and prompt for first question input
    qstn = make_introduction()

    # run q&a loops
    while qstn != 'exit':
        qstn = process_questions(qstn)

    # time to go
    if qstn == 'exit':
        print('\nThank you!  Goodbye.\n')
        sys.exit(0)


if __name__ == '__main__':
    main()
