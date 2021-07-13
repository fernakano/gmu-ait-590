"""
job_sentiment.py
Lib to get sentiment analysis for the project, this can be imported in main project as support functions

"""

from nltk.sentiment.vader import SentimentIntensityAnalyzer


def get_sentiment_score(sentence):
    """
    Return a dictionary with the sentiment analysis of the input sentence.

    This passes through a SentimentIntensityAnalyzer and retrieves the scores

    should have following format
    sentiment_dict: {
                     'compound': 0.7149,
                     'neg': 0.071,
                     'neu': 0.674,
                     'pos': 0.254
                     }

    :param sentence:
    :return sentiment_dict:
    """
    sid = SentimentIntensityAnalyzer()
    ss = sid.polarity_scores(sentence)
    sentiment_dict = {}
    # for k in sorted(ss):
    #     sentiment_dict[k] = ss[k]
    # Parsing sentiment scores manually so its easier refactor in the future if we move away from vader.
    sentiment_dict = {
        'compound': ss['compound'],
        'neg': ss['neg'],
        'neu': ss['neu'],
        'pos': ss['pos']
    }
    return sentiment_dict


def is_sentiment_positive(sentiment_dict):
    """
    Return a True if sentiment is positive based on compound sentiment.
    :param sentiment_dict:
    :return:
    """
    if sentiment_dict['compound']:
        return sentiment_dict['compound'] > 0


def get_sentiment_as_string(boolean_sent):
    """
    Receives the Sentiment from (is_sentiment_positive)
    True if Positive
    False if Negative
    and convert to string
    :param boolean_sent:
    :return:
    """
    return 'Positive' if is_sentiment_positive(boolean_sent) else 'Negative'


# This only gets executed if this file is executed directly and not executed when imported.
def tests():
    """
    Test function, the following should pass to consider the analyzer correct.
    :return:
    """
    test_sentences = [
        ["There was a teammate that never liked anyone's idea, so to deal with that i talked to him to understand "
         "what was the problem. It turns out he had a personal problem at home, so things were great after that "
         "and he was glad that i reached out to him to help! ", "Positive"],

        ["There was a teammate that never liked anyone's idea, so to deal with that, i called in for a meeting "
         "and told him he was a really bad work team mate and i didn't want to work with him anymore.", "Negative"],

        ["There was a teammate that never liked anyone's idea, so to deal with that, i called HR to complain "
         "about his behaviour", "Negative"],

        ["There was a teammate that never liked anyone's idea, so i offered some tips to improve his relationship "
         "with other teammates and he thanked me for helping him!", "Positive"]
    ]

    print("Starting Tests:")
    for sentence in test_sentences:
        ss = get_sentiment_score(sentence[0])
        print("SENTENCE:", sentence[0])
        print("SENTIMENT_SCORES:", ss)
        print("SENTIMENT:", get_sentiment_as_string(ss))
        print("TEST:", 'Pass' if get_sentiment_as_string(ss) == sentence[1] else 'Fail')
        print()


if __name__ == '__main__':
    tests()
