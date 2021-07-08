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
Description:

BONUS Functionality:  Use SpaCy's NER to perform advanced
entity recognition to assist with improved question understanding
and accuracy of answers!

Example Output:

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
nlp = en_core_web_sm.load() # load here, takes a sec


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
        print(f'entity: {entity}, ({entity.label_})')

    if nes == []:
        print(f'no named entities found for {qstn}')

    return nes


def query_wiki(qstn, nes):
    '''query our data sources online, return text result'''

    long_answer = ''
    summaries = []

    # wikipedia/google queries
    for ne in nes:
        #print(f'querying on ne {ne.text}')
        titles = wikipedia.search(ne.text)
        for t in titles:
            try:
                page = wikipedia.page(t)
                summaries.append(wikipedia.summary(t, sentences=1))
            except Exception as e:
                pass

        #print(f'Summaries:')
        #for s in summaries:
        #    print(s[0:50])
    
    if summaries == []:
        # try the nouns if no results with entity search
        mytext = nlp(qstn)
        nouns = [x for x in mytext if x.pos_ == 'NOUN']
        #print('Found Nouns:')
        #print(nouns)
        for n in nouns:
            try:
                page = wikipedia.page(n.text)
                summaries.append(wikipedia.summary(n.text, sentences=1))
            except Exception as e:
                print(f'in noun try, failed: {e}')

    return summaries


def answer_who(qstn, nes, long_answer):
    ''' handle questions beginning with "who" '''

    answer = long_answer[0] # default

    # TODO: formulate a number of "who" answers around the NE or Noun results for XYZ
    # 1. who is XYZ: XYZ is|was ABC (first summary on XYZ?)
    # 2. who <VERB> XYZ: ABC <VERBED> XYZ (lemmatize and form answer?)
    # 3. who is the XYZ: ABC is the XYZ (substitute the name for "who")
    # 4. else "I don't know"
    
    print(answer)
    return answer


def answer_what(qstn, nes, long_answer):
    ''' handle questions beginning with "what" '''

    # TODO: formulate a number of "what" questions/answers around the NEs
    # 1. what is the|a XYZ: XYZ is ABC (maybe first summary?)
    # ...

    answer = 'ABC answer'
    return answer


def answer_when(qstn, nes, long_answer):
    ''' handle questions beginning with "when" '''

    # TODO: formulate a number of "when" questions/answers around the NEs
    # 1. when is XYZ: XYZ is at|on|after|during|in ABC
    # ...

    answer = 'ABC answer'
    return answer


def answer_where(qstn, nes, long_answer):
    ''' handle questions beginning with "where" '''

    # TODO: formulate a number of "where" questions/answers around the NEs
    # 1. where is the XYZ: XYZ is in|at|on (the)+ ABC
    # ...

    answer = 'ABC answer'
    return answer


def get_answer(qstn):
    '''use online resources to try to answer question.'''

    # get Named Entitiess from spacy
    nes = get_nes(qstn)
    
    # query for data with named entities (or nouns if no NEs)
    long_answer = query_wiki(qstn, nes)
    
    # handle no results
    if long_answer == []:
        # we have no results to parse, return idk
        return "I'm sorry, I do not know the answer."

    # look up an answer to the question:
    # TODO: lookup an answer, return 'some answer for now'

    # get the first word
    w_word = re.match(r"^([\w\-]+)", qstn.lower())
    
    # answer depending on first word (who/what/where/when)
    if w_word.group().lower() == 'who':
        # TODO: handle 'who' type questions
        print('WHO!')
        ans = answer_who(qstn, nes, long_answer)

    elif w_word.group().lower() == 'what':
        # TODO: handle 'what' type questions
        print('WHAT!')
        ans = answer_what(qstn, nes, long_answer)

    elif w_word.group().lower() == 'where':
        # TODO: handle 'where' type questions
        ans = answer_where(qstn, nes, long_answer)
        print('WHERE!')

    elif w_word.group().lower() == 'when':
        # TODO: handle 'when' type questions
        ans = answer_when(qstn, nes, long_answer)
        print('WHEN!')

    else:
        print('ERROR--should not get here...')
        assert False    

    return ans


def answer_questions(qstn):
    ''' determine question and look up/return answer'''

    # validate question begins with who, what, when, or where
    if not qstn_is_valid(qstn):
        ans = 'I am sorry, I can only answer questions starting with '
        ans += 'Who, What, When or Where.' 

    else:
        # try to find an answer
        ans = get_answer(qstn)  

    # respond and get next question        
    qstn = input(f'=>  {ans}\n\n=?> ')
    
    return qstn


def main():
    print('hello!')

    # introduction and prompt for first question input
    qstn = make_introduction()
    
    # run q&a loops
    while qstn != 'exit':
        qstn = answer_questions(qstn)
    
    # time to go
    if qstn == 'exit':
        print('\nThank you!  Goodbye.\n')
        sys.exit(0)


if __name__ == '__main__':
    main()