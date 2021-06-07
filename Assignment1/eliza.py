import re

from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

# DEFAULTS
CONVERSATION_STARTER = "Hi, I'm a psychotherapist. What is your name?"
USER_NAME = "Unnamed"

RULES = {
    r".*name.*\b(\w+)$": {'type': 'name', 'responses': ['Hi {{NAME}}. How can I help you today?']},
    r".*want.*": {'type': 'want', 'responses': ["Hi {{NAME}}, do {}?", "Hey {{NAME}}, why do {}?"]},
    r".*crave.*": {'type': 'want', 'responses': ["Hi {{NAME}}, tell me more about your cravings..."]},
    r"(.*)": {'type': 'unknown', 'responses': ["Hi {{NAME}} I didn't quite understand, can you say that another way?"]}
}

RESPONSE_CONVERTERS = {
    r'i': 'you'
}


def main():
    response = CONVERSATION_STARTER
    while True:
        response = input("[Eliza]: " + response + "\n[User]: ")
        if response == 'exit':
            break
        response = process(response)


def process(text):
    global USER_NAME
    tokens = normalize_and_tokenize(text)
    text = convert_response_as_text(tokens)
    for regex, rule in RULES.items():
        matches = re.match(regex, text)
        if matches:
            if rule['type'] == 'name':
                USER_NAME = matches[matches.lastindex if matches.lastindex else 0]
            sentence = rule['responses'][0].replace("{{NAME}}", USER_NAME)
            sentence = sentence.format(matches[matches.lastindex if matches.lastindex else 0])
            return sentence


def normalize_and_tokenize(text):
    tokens = word_tokenize(text.lower())
    return tokens


# for this scenario, maybe string split() could possibly be enough.
def word_tokenize(text):
    tokenizer = RegexpTokenizer(r'\w+')
    return tokenizer.tokenize(text)


def convert_response_as_text(tokens):
    return " ".join(response_parser(tokens))


def response_parser(tokens):
    for i, j in enumerate(tokens):
        for convert_from, convert_to in RESPONSE_CONVERTERS.items():
            tokens[i] = re.sub(convert_from, convert_to, tokens[i])
    return tokens


if __name__ == "__main__":
    main()
