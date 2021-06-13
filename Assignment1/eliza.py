import re
import random

from nltk.tokenize import RegexpTokenizer

# DEFAULTS
CONVERSATION_STARTER = "Hi, I'm a psychotherapist. What is your name?"
USER_NAME = "Friend"

RULES = {
    r".*name.*\b(\w+)$": {
        'type': 'name',
        'responses': [
            'Hi {{NAME}}. How can I help you today?'
        ]},
    r"\byes\b|\bno\b": {
        'type': 'short_ans',
        'responses': [
            'Tell me more, {{NAME}}',
            'Do go on, {{NAME}}',
            '{{NAME}}, can you expand on that?'
        ]},
    r"(.*want.*)": {
        'type': 'want',
        'responses': [
            "Hi {{NAME}}, do {}?",
            "Hey {{NAME}}, why do {}?"
        ]},
    r"(.*crave.*)": {
        'type': 'want',
        'responses': [
            "Hi {{NAME}}, tell me more about your cravings..."
        ]},
    r".*am.*|.*i have been.*": {
        'type': 'am',
        'responses': [
            "Hi {{NAME}}, why do you think that is?",
            "How does being {} make you feel?"
        ]},
    r".*dunno.*|.*idk.*|i don\t know": {
        'type': 'idk',
        'responses': [
            "{{NAME}}, maybe you do know--can you tell me?",
            "Can you do your best to explain, {{NAME}}?"
        ]},
    r".*feel.*": {
        'type': 'feels',
        'responses': [
            "{{NAME}}, what is making {}?",
            "Why do you think {}, {{NAME}}"
        ]},
    r"what is (.*)|(how to make.*)": {
        'type': 'question',
        'responses': [
            "You can see it here: www.google.com?q={}"
        ]},
    r"(.*)": {
        'type': 'unknown',
        'responses': [
            "Hi {{NAME}}, I didn't quite understand, can you say that another way?",
            "I think you're saying {}, is that right?"
        ]}
}

RESPONSE_CONVERTERS = {
    r'\bi\b|\bme\b': 'you',  # surrounding 'i' with word boundaries so we don't replace 'i' in other words
    r"\bmy\b|\bour\b": 'your',  # replace my/our with 'your'
}


def main():
    input_text = CONVERSATION_STARTER
    print(f'\nWelcome to your therapist--to end, simply type "exit"...\n')
    while True:
        input_text = input(f'[Eliza]: ' + input_text + f'\n[{USER_NAME}]: ')
        if input_text.lower() in ['exit', 'quit', 'bye', 'goodbye']:
            print(f'Farewell {USER_NAME}, take care!\n')
            break
        input_text = process(input_text)


def process(user_input):
    global USER_NAME
    tokens = normalize_and_tokenize(user_input)
    text = convert_response_as_text(tokens)
    for regex, rule in RULES.items():
        matches = re.match(regex, text, re.IGNORECASE)
        if matches:
            if rule['type'] == 'name':
                USER_NAME = matches[matches.lastindex if matches.lastindex else 0].capitalize()
            sentence = random.choice(rule['responses']).replace("{{NAME}}", USER_NAME)
            # TODO: switch convert place converted_string = matches[matches.lastindex if matches.lastindex else 0]
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
    tokens_1 = change_perspective(tokens)
    return " ".join(tokens_1)


def change_perspective(tokens):
    for i, j in enumerate(tokens):
        for convert_from, convert_to in RESPONSE_CONVERTERS.items():
            tokens[i] = re.sub(convert_from, convert_to, tokens[i], flags=re.IGNORECASE)
    return tokens


if __name__ == "__main__":
    main()
