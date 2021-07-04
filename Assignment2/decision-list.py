###############################################################################
# Group 3                                                                     #
# Assignment 2 - WSD                                                          #
#  Assuming you have python 3                                                 #
# TO EXECUTE RUN:                                                             #
#  python decision-list.py line-train.xml line-test.xml my-decision-list.txt  #
###############################################################################
import math
import pprint
import sys

from bs4 import BeautifulSoup
from nltk import RegexpTokenizer, ConditionalFreqDist, ConditionalProbDist, ELEProbDist
# from nltk.probability import ConditionalProbDist, ELEProbDist
from nltk.corpus import stopwords

pp = pprint.PrettyPrinter(indent=4)

# Word to disabiguate
a_word = "line"

# Collocation range
collocation_windows = [-2, -1, 1, 2]


# Read Arguments from the input on the required order
def read_arguments():
    return sys.argv[1], sys.argv[2], sys.argv[3]


# Read XML files
def read_xml(xml_file):
    return BeautifulSoup(open(xml_file, 'r'), 'xml')


# normalize_and_tokenize function tokenize text and set them in lowercase
def normalize_and_tokenize(text):
    """
    This function will Lower the text and call the word_tokenizer(text) to retrieve the tokenized lower case text
    then remove stop words
    :param text:
    :return: lowered tokenized text.
    """
    text = text.lower()
    text = text.replace("lines", "line")
    tokens = word_tokenize(text)
    tokens = [token for token in tokens if token not in stopwords.words('english')]
    return tokens


def word_tokenize(text):
    """Work Tokenizer
        This Tokenizer will user a RegexpTokenizer \w+
        to identify words from the sentences, this will exclude punctuations and special characters while tokenizing words.

    :param text:
    :return: tokenized text
    """
    tokenizer = RegexpTokenizer(r'\w+')
    return tokenizer.tokenize(text)


def get_word_index(word_list, word):
    try:
        index = word_list.index(word)
    except ValueError:
        index = None
        print(f'Warning from get_word_index: Did not find word_list.index(word) for {word}')
    return index


#
def create_training_dict_from_xml(xml):
    training_dict = list()
    for instance in xml.find_all("instance"):
        tokens = list()
        
        for sentence in instance.context.find_all('s'):
            tokens.extend(normalize_and_tokenize(sentence.get_text()))

        line = {
            'id': instance['id'],
            'sense': instance.answer['senseid'] if instance.answer else 'to_predict',
            'tokens': tokens
        }

        training_dict.append(line)
    return training_dict


def create_collocation_distribution(training_dict):
    # Set the collocation range
    # collocation_windows = [-2, -1, 1, 2]

    # create a ConditionalFreqDist to Measure Collocational Distribution
    collocation_distribution = ConditionalFreqDist()

    # Starting Collocational distribution counts
    # for each instance of the training data
    for instance in training_dict:
        sense, tokens = instance['sense'], instance['tokens']
        # find the index of the ambiguous word "a_word"
        index = get_word_index(tokens, a_word)

        # if word exists in list of tokens
        if index:
            # start processing the collocation collocation_windows
            for window in collocation_windows:
                # for each window (-2, -1, +1, +2) define a range
                w_range = range(window, 0) if window < 0 else range(1, window + 1)

                # for each window(w) in the window range find the context and append to the collocation.
                # range is used just to make it easier to travel the collocation_windows
                collocation = ''
                # +/- k references on Step 3 of Yarowski article.
                for k in w_range:
                    context_index = index + k
                    if 0 <= context_index <= len(tokens) - 1:
                        collocation = collocation + tokens[context_index] + ' '
                    else:
                        pass
                        # print('notInList')

                # decide to append real a_word depending on the window
                if window < 0:
                    collocation = collocation + str(tokens[index])
                else:
                    collocation = str(tokens[index]) + ' ' + collocation

                # add to the freq_distribution
                # NOT SURE OF THIS IF WE NEED TO HAVE BOTH +/- W with collocation
                # collocation_distribution[str(window) + 'W ' + collocation][sense] += 1
                collocation_distribution[str(window) + 'W ' + collocation.rstrip()][sense] += 1
    return collocation_distribution


# Step 4 of the Article
def create_decision_list_from_conditinal_prob(cpdist):
    decision_list = []
    # calculate log likelihood
    for position in cpdist.conditions():
        # print(position)
        ratio = cpdist[position].prob('phone') / cpdist[position].prob('product')
        if ratio == 0:
            likelihood = 0
        else:
            likelihood = math.log(ratio, 2)
        classification = 'phone' if ratio >= 1 else 'product'
        decision_list.append({'position': position, 'likelihood': abs(likelihood), 'classification': classification})

    return sorted(decision_list, key=lambda i: i['likelihood'], reverse=True)


def lookup_decision_list(decision_list, value):
    return list(filter(lambda dl: dl['position'] in [value], decision_list))


#####################################################
#    Main Execution for Decision List stats here    #
#####################################################
def main():
    print("Starting Decision List")
    line_train, line_test, decision_list_output = read_arguments()

    # Read the XML input line_train.xml file
    xml = read_xml(line_train)

    # Create training dict from training data xml
    training_dict = create_training_dict_from_xml(xml)

    # create a ConditionalFreqDist to Measure Collocational Distribution
    collocation_distribution = create_collocation_distribution(training_dict)
    # pp.pprint(list(sorted(collocation_distribution.items())))
    # collocation_distribution.plot()

    cpdist = ConditionalProbDist(collocation_distribution, ELEProbDist, 10)
    # pp.pprint(list(cpdist.conditions()))
    # pp.pprint(list(cpdist.items()))

    # create decision list using ConditionalProbDist as on the hints and tips.
    decision_list = create_decision_list_from_conditinal_prob(cpdist)
    # pp.pprint(decision_list)

    # write decision list to file
    # type(decision_list) is a list, each element containing a dict like this:
    # {'position': '-2W man end line', 'likelihood': 2.321928094887362, 'classification': 'phone'}
    # TODO: Deleteme:  with open ('my-decision-list.txt', 'w') as f:
    with open(decision_list_output, 'w') as f:
        for eachline in decision_list:
            f.write(str(eachline))
            f.write('\n')

    ##########################
    # START TESTING DATA     #
    ##########################
    xml_test = read_xml(line_test)
    testing_dict = create_training_dict_from_xml(xml_test)  # a list

    # validating testing dict so I can validate results
    print(f'testing_dict:  {type(testing_dict)}, len {len(testing_dict)}')
    assert len(testing_dict) == 126, f"Only found {len(xml_test)} lines in test dataset"

    # for each instance of the training data
    unknown_sense = 'product'
    count_phone = 0
    count_product = 0
    # Find the most common sense
    for instance in training_dict:
        if instance['sense'] == 'phone':
            count_phone += 1
        else:
            count_product += 1

    # unknown_sense will be default sense, when sense is ambiguous
    if count_phone > count_product:
        unknown_sense = 'phone'

    testing_results = []
    for instance in testing_dict:
        sense_lookups = []
        max_likelihood = {}
        instance_id, tokens = instance['id'], instance['tokens']
        index = get_word_index(tokens, a_word)
        # if word exists in list of tokens
        if index:
            # start processing the collocation collocation_windows
            for window in collocation_windows:
                # for each window (-2, -1, +1, +2) define a range
                w_range = range(window, 0) if window < 0 else range(1, window + 1)

                # for each window(w) in the window range find the context and append to the collocation.
                # range is used just to make it easier to travel the collocation_windows
                collocation = ''
                # +/- k references on Step 3 of Yarowski article.
                for k in w_range:
                    context_index = index + k
                    if 0 <= context_index <= len(tokens) - 1:
                        collocation = collocation + tokens[context_index] + ' '
                    else:
                        pass
                        # print('notInList')

                # decide to append real a_word depending on the window
                if window < 0:
                    collocation = collocation + str(tokens[index])
                else:
                    collocation = str(tokens[index]) + ' ' + collocation
                position = str(window) + 'W ' + collocation.rstrip()
                likelihood = lookup_decision_list(decision_list, position)
                if max_likelihood == {} and len(likelihood) > 0:
                    max_likelihood = likelihood[0]
                elif max_likelihood == {} and len(likelihood) == 0:
                    max_likelihood = {'position': position, 'likelihood': 0, 'classification': unknown_sense}
                elif len(likelihood) > 0:
                    max_likelihood = likelihood[0] if likelihood[0]['likelihood'] > max_likelihood[
                        'likelihood'] else max_likelihood
                # else:
                #     max_likelihood = {'position': position, 'likelihood': 0, 'classification': unknown_sense}
            # sense_lookups.append(max_likelihood)
            testing_results.append({'id': instance_id, 'sense': max_likelihood['classification']})

    # validate our test output:
    warn_str = f"WARNING: testing_results has {len(testing_results)} elements, expected {len(testing_dict)}"
    assert len(testing_results) == len(testing_dict), warn_str
    # for each instance on the test data, lookup the likelihood from the decision table for each collocation +/- k
    # at the end of the collection, choose the item with the highest likelihood.

    # if no item is found in decision table, use the sense with highest probability.
    #
    # ...
    #
    # create scorer.py
    # display confusion matrix
    with open('my-line-answers.txt', 'w') as f:
        for item in testing_results:
            result = f'<answer instance="{item["id"]}" senseid="{item["sense"]}"/>'
            # print(result)
            f.write(result)
            f.write('\n')
    print("done")


if __name__ == "__main__":
    main()
