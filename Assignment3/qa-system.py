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

BONUS Functionality:

Example Output:

"""
import sys
import wikipedia
import re


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
    if re.match(r"^([W|w]hen|[W|w]here|[W|w]ho|[W|w]hat)\b", qstn):
        return True
    else:
        print('baa--wrong start!')
        return False


def get_answer(qstn):
    '''use online resources to try to answer question.'''

    # look up an answer to the question:
    # TODO: lookup an answer, return 'some answer for now'
    return 'some answer for now'


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