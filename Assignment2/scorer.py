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
from bs4 import BeautifulSoup
from nltk import ConfusionMatrix

def read_inputs():
    '''
    given input filenames as args, read their contents as two lists.
    input format looks like this:
    <answer instance="line-n.art7} aphb 20801955:" senseid="phone"/>
    '''
    my_line_ans_file = sys.argv[1]
    line_ans_file = sys.argv[2]

    my_answers_file = BeautifulSoup(open(my_line_ans_file, 'r'), 'html.parser')
    true_answers_file = BeautifulSoup(open(line_ans_file, 'r'), 'html.parser')

    return my_answers_file, true_answers_file


def debug_show_three_dict_items(comparison_dict):
    '''just a helper if we want to see what's in the dictionary'''
    # DEBUG: sample of 3 entries in our comparison dict:
    three_keys = list(comparison_dict.keys())[:3]
    print('First three elements in the dictionary:')
    for k in three_keys:
        print(comparison_dict[k])


def gather_answers(my_answers, true_answers):
    '''compare line-by-line, my-line-answers and line-answers'''
    iterations = max(len(my_answers), len(true_answers)) # number instances to compare
    
    # Make a dict to hold predictions and ground truth like this:
    # "instance": {"true_label": true_sense, "my_label": my_sense}
    # Sample entries to parse: 
    # <answer instance="line-n.art7} aphb 20801955:" senseid="product"/>
    # <answer instance="line-n.w7_126:14239:" senseid="product"/>
    comparison_dict = defaultdict(list)

    #pull out our line predictions
    for answer in my_answers.find_all('answer'):
        comparison_dict[answer['instance']] = {'my_label': answer['senseid']}

    for answer in true_answers.find_all('answer'):
        # grab the previous my_label value and make a bigger comparison dict item
        my_label = comparison_dict[answer['instance']]['my_label']
        comparison_dict[answer['instance']].update({'my_label': my_label, 'true_label': answer['senseid']})

    return comparison_dict


def compare_labels(comparison_dict):
    '''return a confusion matrix and the overall accuracy of our predictions'''
    my_labels = []
    true_labels = []
    correct_count = 0
    total_count = 0

    #collect all the labels into lists for the CM and accuracy metrics
    for instance, label_dict in comparison_dict.items():
        my_label = label_dict['my_label']
        my_labels.append(my_label)
        true_label = label_dict['true_label']
        true_labels.append(true_label)
        if my_label == true_label:
            correct_count += 1
        total_count += 1

    # build the confusion matrix
    confusion_mtx = ConfusionMatrix(list(true_labels), list(my_labels))

    # calculate accuracy
    accuracy = round(correct_count*1.0/total_count, 4)

    return accuracy, confusion_mtx

        

def main():
    # handle calls from decision-list directly: 
    # expect call with args scorer.py my-line-answers.txt line-answers.txt
    if len(sys.argv) != 3:
        sys.argv[1] = 'my-line-answers.txt'
        sys.argv[2] = 'line-answers.txt'

    # get input data
    my_answers, true_answers = read_inputs()

    # collect our results next to the true answers
    comparison_dict = gather_answers(my_answers, true_answers)

    # compare key-value sets in each element of the comparison dict.  
    acc, cm = compare_labels(comparison_dict)

    print(f'\nOur Decision List Accuracy: {acc*100} %')
    print('\n ----- Confusion Matrix ----- ')
    print(cm)


    # TODO: decide w/ team how we hand this back to decision-list.py/print outputs...
    # TODO: finalize comments, check rubric


if __name__ == "__main__":
    main()