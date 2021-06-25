#####################################################
#    Main Execution for Decision List stats here    #
#
#  Assuming you have python 3
# TO EXECUTE RUN:
#  python decision-list.py line-train.xml line-test.xml my-decision-list.txt
#
#####################################################
import pprint
import sys

from bs4 import BeautifulSoup
from nltk import RegexpTokenizer, ConditionalFreqDist
from nltk.corpus import stopwords

pp = pprint.PrettyPrinter(indent=4)

# Word to disabiguate
a_word = "line"


def main():
    print("Starting Decision List")
    line_train, line_test, decision_list = read_arguments()

    # Read the XML input line_train.xml file
    xml = read_xml(line_train)

    # Create training dict from training data xml
    training_dict = create_training_dict_from_xml(xml)

    # Set the collocation range
    windows = [-2, -1, 1, 2]

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
            # start processing the collocation windows
            for window in windows:
                # for each window define a range
                w_range = range(window, 0) if window < 0 else range(1, window + 1)

                # for each window(w) in the window range find the context and append to the collocation.
                collocation = ''
                for w in w_range:
                    context_index = index + w
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
                collocation_distribution[str(window) + 'W ' + collocation][sense] += 1
    pp.pprint(list(sorted(collocation_distribution.items())))
    collocation_distribution.plot()
    # calculate log likelihood
    # ....
    # create decision list using ConditionalProbDist as on the hints and tips.
    #
    # use decision list to test the test data
    # ...
    #
    # create scorer.py
    # display confusion matrix

    print("done")


def get_word_index(word_list, word):
    try:
        index = word_list.index(word)
    except ValueError:
        index = None
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
            'sense': instance.answer['senseid'],
            'tokens': tokens
        }

        training_dict.append(line)
    return training_dict


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
    tokens = word_tokenize(text.lower())
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


if __name__ == "__main__":
    main()
