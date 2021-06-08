import re
import random

from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

# DEFAULTS
CONVERSATION_STARTER = "Hi, I'm a psychotherapist. What is your name?"
USER_NAME = "friend"

RULES = {
    r".*name.*\b(\w+)$": {'type': 'name', 'responses': ['Hi {{NAME}}. How can I help you today?']},
    r"\byes\b|\bno\b": {'type': 'short_ans', 'responses': ['Tell me more, {{NAME}}', 'Do go on, {{NAME}}',
                                                           '{{NAME}}, can you expand on that?']},
    r".*want.*": {'type': 'want', 'responses': ["Hi {{NAME}}, do {}?", "Hey {{NAME}}, why do {}?"]},
    r".*crave.*": {'type': 'want', 'responses': ["Hi {{NAME}}, tell me more about your cravings..."]},
    r".*am.*|.*have been.*": {'type': 'am', 'responses': ["Hi {{NAME}}, why do you think that is?"]},
    r".*dunno.*|.*idk.*": {'type': 'idk', 'responses': ["{{NAME}}, maybe you do know--can you tell me?",
                                                        "Can you do your best to explain, {{NAME}}?"]},
    r".*feel.*": {'type': 'feels', 'responses': ["{{NAME}}, what is making {}?", "Why do you think {}, {{NAME}}"]},
    r"(.*)": {'type': 'unknown', 'responses': ["Hi {{NAME}}, I didn't quite understand, can you say that another way?",
                                               "I think you're saying {}, is that right?"]}
}

RESPONSE_CONVERTERS = {
    r'\bi\b|\bme\b': 'you',  # surrounding 'i' with word boundaries so we don't replace 'i' in other words
    r"\bmy\b|\bour\b": 'your'  # replace my/our with 'your'
}


def main():
    response = CONVERSATION_STARTER
    print(f'\nWelcome to your therapist--to end, simply type "exit"...\n')
    while True:
        response = input("[Eliza]: " + response + "\n[User]: ")
        if response.lower() in ['exit', 'quit', 'bye', 'goodbye']:
            print(f'Farewell {USER_NAME}, take care!\n')
            break
        response = process(response)


def process(text):
    global USER_NAME
    tokens = normalize_and_tokenize(text)
    text = convert_response_as_text(tokens)
    for regex, rule in RULES.items():
        matches = re.match(regex, text, re.IGNORECASE)
        if matches:
            if rule['type'] == 'name':
                USER_NAME = matches[matches.lastindex if matches.lastindex else 0]

            # choose randomly from possible responses
            choice = 0  # default to first element in responses list
            if len(rule['responses']) > 1:
                choice = random.randint(0, len(rule['responses']) - 1)

            sentence = rule['responses'][choice].replace("{{NAME}}", USER_NAME)
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
    return " ".join(change_perspective(tokens))


def change_perspective(tokens):
    for i, j in enumerate(tokens):
        for convert_from, convert_to in RESPONSE_CONVERTERS.items():
            tokens[i] = re.sub(convert_from, convert_to, tokens[i], flags=re.IGNORECASE)
    return tokens


if __name__ == "__main__":
    main()
