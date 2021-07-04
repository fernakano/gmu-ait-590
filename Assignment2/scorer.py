###############################################################################
# Group 3                                                                     #
# Assignment 2 - WSD                                                          #
#  Assuming you have python 3                                                 #
# TO EXECUTE RUN:                                                             #
#  python scorer.py my-line-answers.txt line-answers.txt                      #
###############################################################################

'''
scorer.py is a utility function to support evaluation of the output of decision-list.py.  
scorer.py takes as input our sense tagged output (my-line-answers.txt) and 
compares it with the gold standard "key" data in line-answers.txt. scorer.py
reports the overall accuracy of our tagging, and provides a confusion matrix similar to the one found
on page 156 of JM. This program should write output to STDOUT. 
'''
import re
import sys
from collections import defaultdict

def read_inputs():
    '''
    given input filenames as args, read their contents as two lists.
    input format looks like this:
    <answer instance="line-n.art7} aphb 20801955:" senseid="phone"/>
    '''
    my_line_ans_file = sys.argv[1]
    line_ans_file = sys.argv[2]
    print(my_line_ans_file, line_ans_file)

    # SAMPLE READING WITH BS
    from bs4 import BeautifulSoup

    xml_my_line_ans_file = BeautifulSoup(open(my_line_ans_file, 'r'), 'html.parser')
    xml_line_ans_file = BeautifulSoup(open(line_ans_file, 'r'), 'html.parser')

    for answer in xml_my_line_ans_file.find_all('answer'):
        print(f'myanswer: {answer["instance"]} sense: {answer["senseid"]}')

    for answer in xml_line_ans_file.find_all('answer'):
        print(f'trueanswer: {answer["instance"]} sense: {answer["senseid"]}')
    # SAMPLE READING WITH BS


    # read the input files
    with open(my_line_ans_file, 'r') as f:
        my_answers_list = f.readlines()
    
    with open(line_ans_file, 'r') as f:
        true_answers_list = f.readlines()

    return my_answers_list, true_answers_list


def gather_answers(my_answers, true_answers):
    # compare line-by-line, my-line-answers and line-answers
    iterations = max(len(my_answers), len(true_answers)) # number instances to compare
    
    # Make a dict to hold predictions and ground truth like this:
    # "instance": {"true_label": true_sense, "my_label": my_sense}
    # Sample entry to parse: 
    # <answer instance="line-n.art7} aphb 20801955:" senseid="product"/>
    # <answer instance="line-n.w7_126:14239:" senseid="product"/>
    comparison_dict = defaultdict(list)

    # pull out the true line labels
    for line in true_answers:
        try:
            _, instance, sense = line.split()
            true_instance = re.search('\"(.*):\"', instance).group(1)
            true_sense = re.search('\"(.*)\"', sense).group(1)
            comparison_dict[true_instance] = [{'true_label': true_sense}]
        except Exception as e:
            pass
    
    # pull out our line predictions
    for line in my_answers:
        try:
            _, instance, sense = line.split()
            my_instance = re.search('\"(.*):\"', instance).group(1)
            my_sense = re.search('\"(.*)\"', sense).group(1)
            comparison_dict[my_instance].extend([ {'my_label': my_sense}])
        except Exception as e:
            print(f'could not pull out my_answer info: {e}')
            print(f'^^ line was {line} ^^')

    return comparison_dict

def main():
    print("hello!")
    # get input data
    my_answers, true_answers = read_inputs()



    print(len(my_answers), len(true_answers))
    print('My first answer: ', my_answers[0])
    print('True first answer: ', true_answers[0])

    # collect our results next to the true answers
    comparison_dict = gather_answers(my_answers, true_answers)

    # TODO: compare key-value sets in each element of the comparison dict.  
    # TODO: create the confusion matrix
    # TODO: determine the overall accuracy
    # TODO: decide w/ team how we hand this back to decision-list.py/print outputs...
    
    # DEBUG: sample of 3 entries in our comparison dict:
    three_keys = list(comparison_dict.keys())[:3]
    for k in three_keys:
        print(comparison_dict[k])

if __name__ == "__main__":
    main()