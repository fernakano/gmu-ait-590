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
    r".*suicid.*|.*kill.*": {
        'type': 'alert',
        'responses': [
            "{{NAME}}, you can reach the National Suicide Prevention Lifeline night or day: 800-273-8255"
        ]},
    r"\byes\b|\bno\b": {
        'type': 'short_ans',
        'responses': [
            'Tell me more, {{NAME}}',
            'Do go on, {{NAME}}',
            '{{NAME}}, can you expand on that?',
            'are you sure?'
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
    r"(.*i am.*|.*i.m.*|.*i have been.*)": {
        'type': 'am',
        'responses': [
            "Hi {{NAME}}, why do you think {}?",
            "How does being {} make you feel?"
        ]},
    r"(because.*)": {
        'type': 'explain',
        'responses': [
            "No way... just {}?"
        ]},
    r".*dunno.*|.*idk.*|.*i don.t know.*|.*i dont know.*": {
        'type': 'explain',
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
    r".*think(.*)": {
        'type': 'feels',
        'responses': [
            "Why do you think that {}?"
        ]},
    r"what is (.*)|(how to make.*)|(how do i make.*)": {
        'type': 'question',
        'responses': [
            "You can see it here: www.google.com?q={}"
        ]},
    r"(.*thanks.*)": {
        'type': 'compliment',
        'responses': [
            "No problem {{NAME}}, I'm glad to help",
            "No problem, I hope I was able to meet your expectations...",
            "Hey {{NAME}}, Don't worry.. I'm here for this"
        ]},
    r"(.*how are you.*)": {
        'type': 'question',
        'responses': [
            "I'm doing great! how about you?"
        ]},
    r"exit|quit|bye|goodbye": {
        'type': 'exit',
        'responses': [
            "Farewell {{NAME}}, take care!"
        ]},
    r"^(?![\s\S])": {
        'type': 'exit',
        'responses': [
            "{{NAME}}, are you there?",
            "...?",
            "Feel free to open up, I'm not going to judge you..."
        ]},
    # last-case catch-all rule, when no rule could be matched:
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
    r"\bam\b|\bm\b": 'are',
    r"\bmyself\b": 'yourself'
}


def is_valid(input_text):
    if input_text.strip(' ') == '':
        return True
    # check for only numbers and symbols:
    word_tokens = word_tokenize(input_text)
    for word in word_tokens:
        if word.isalpha():
            return True
    else:
        return False


def main():
    print(
          '******************************************************************\n'
          '*                                                                *\n'
          '*    Welcome to your therapist--to end, simply type "exit"...    *\n'
          '*                                                                *\n'
          '******************************************************************'
          )

    message = CONVERSATION_STARTER
    while True:
        input_text = input(f'[Eliza]: ' + message + f'\n[{USER_NAME}]: ')
        if not is_valid(input_text):
            message = f"I cannot understand '{input_text}'"
            continue

        message = process(input_text)
        if input_text.lower() in ['exit', 'quit', 'bye', 'goodbye']:
            print('[Eliza]: ' + message)
            break


def process(user_input):
    global USER_NAME
    normalized_user_input = " ".join(normalize_and_tokenize(user_input))
    for regex, rule in RULES.items():
        matches = re.match(regex, normalized_user_input, re.IGNORECASE)
        if matches:
            if rule['type'] == 'name':
                USER_NAME = matches[matches.lastindex if matches.lastindex else 0].capitalize()
            sentence = random.choice(rule['responses']).replace("{{NAME}}", USER_NAME)
            # Switch message perspective for last group match
            group_text = matches[matches.lastindex if matches.lastindex else 0]
            group_text_perspective = convert_response_as_text(normalize_and_tokenize(group_text))
            sentence = sentence.format(group_text_perspective)
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
