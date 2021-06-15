#######################################
#                ELIZA                #
# Group 3: Fernando, Melissa, Archer  #
#######################################
import re
import random
from nltk.tokenize import RegexpTokenizer

# DEFAULT VALUES
# Assign initial value to response from Eliza
CONVERSATION_STARTER = "Hi, I'm a psychotherapist. What is your name?"
# user_name is name of the chatbot user, we set the initial value to be "Friend"
USER_NAME = "Friend"

# create a Python Dictionary "Rules" (Kay value pair form)
# It should map all potential dialog scenarios Eliza will encounter, along with
# Eliza's response.
# Regular expressions are used in key value to capture/replace certain words in dialog.
# There are 17 rules so far.
RULES = {
    # Rule to identify user name
    r".*name.*\b(\w+)$": {
        'type': 'name',
        'responses': [
            'Hi {{NAME}}. How can I help you today?'
        ]},
    # Rule to reply help response if user have suicidal or killing thoughts.
    r".*suicid.*|.*kill.*": {
        'type': 'alert',
        'responses': [
            "{{NAME}}, you can reach the National Suicide Prevention Lifeline night or day: 800-273-8255"
        ]},
    # response for short answers
    r"\byes\b|\bno\b|\bright\b|\bnope\b": {
        'type': 'short_ans',
        'responses': [
            'Tell me more, {{NAME}}',
            'Do go on, {{NAME}}',
            '{{NAME}}, can you expand on that?',
            'are you sure?'
        ]},
    # identify user wants.
    r"(.*want.*)": {
        'type': 'want',
        'responses': [
            "Hi {{NAME}}, do {}?",
            "Hey {{NAME}}, why do {}?"
        ]},
    # Word Spot Crave
    r".*crave(.*)|.*craving(.*)": {
        'type': 'want',
        'responses': [
            "Hi {{NAME}}, tell me more about your cravings...",
            "Hi {{NAME}}, tell me more about your craving for {}"
        ]},
    # identify when person is talking something about itself.
    r"(.*i am.*|.*i.m.*|.*i have been.*)": {
        'type': 'am',
        'responses': [
            "Hi {{NAME}}, why do you think {}?",
            "How does being {} make you feel?"
        ]},
    # identify explaining reasoning ideas
    r"(because.*)": {
        'type': 'explain',
        'responses': [
            "No way... just {}?"
        ]},
    # identify user doesnt know what to say about a topic
    r".*dunno.*|.*idk.*|.*i don.t know.*|.*i dont know.*": {
        'type': 'explain',
        'responses': [
            "{{NAME}}, maybe you do know--can you tell me?",
            "Can you do your best to explain, {{NAME}}?"
        ]},
    # identify user sentiments
    r".*feel.*": {
        'type': 'feels',
        'responses': [
            "{{NAME}}, what is making {}?",
            "Why do you think {}, {{NAME}}"
        ]},
    # identify user thoughts
    r".*think(.*)": {
        'type': 'feels',
        'responses': [
            "Why do you think that {}?"
        ]},
    # let user asks questions on what are things and how to make and answer with a google search link
    r"what is (.*)|(how to make.*)|(how do i make.*)": {
        'type': 'question',
        'responses': [
            "You can see it here: www.google.com?q={}"
        ]},
    # identify user acknowledgment of something.
    r"(.*thanks.*)": {
        'type': 'acknowledgment',
        'responses': [
            "No problem {{NAME}}, I'm glad to help, anything else?",
            "No problem, I hope I was able to meet your expectations... Anything else i can help you with?",
            "Hey {{NAME}}, Don't worry.. I'm here for this! what now?"
        ]},
    # identify the user is apologizing for something
    r".*(sorry.*)": {
        'type': 'feels',
        'responses': [
            "Don't worry...  why do you want to apologize?",
        ]},
    # identify when user asks how the bot is.
    r"(.*how are you.*)": {
        'type': 'question',
        'responses': [
            "I'm doing great! how about you?"
        ]},
    # identify break exit options
    r"exit|quit|bye|goodbye": {
        'type': 'exit',
        'responses': [
            "Farewell {{NAME}}, take care!"
        ]},
    # identify when user talks empty information.
    r"^(?![\s\S])": {
        'type': 'none',
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

# Another Dictionary using Regular expression to change perspective in conversation
# switching from first person input text to second person response
RESPONSE_CONVERTERS = {
    r'\bi\b|\bme\b': 'you',  # surrounding 'i' with word boundaries so we don't replace 'i' in other words
    r"\bmy\b|\bour\b": 'your',  # replace my/our with 'your'
    r"\bam\b|\bm\b": 'are',
    r"\bmyself\b": 'yourself',
    r"\bim\b": 'you are',
}


#############################################
#    Main Execution for Eliza stats here    #
#############################################

def main():
    """This is the Main execution function for Eliza

    This is where the execution starts, it will work to process the iterated loop for Eliza Chat Bot.
    The idea is that here we will have an Infinite Loop that is stopped by specific keywords like:
     'exit, quit, bye or goodbye'
    on each iteration of the loop the program will wait for an input from the User with the response process
    from the previous message.
    :return: None
    """
    print(
        '******************************************************************\n'
        '*                                                                *\n'
        '*    Welcome to your therapist--to end, simply type "exit"...    *\n'
        '*                                                                *\n'
        '******************************************************************\n'
    )

    message = CONVERSATION_STARTER
    # While True statement forces it to run unless break
    while True:
        input_text = input(f'[Eliza]: ' + message + f'\n[{USER_NAME}]: ')
        # Validate if input is valid and not a single non alphanumeric text.
        if not is_valid(input_text):
            message = f"I cannot understand '{input_text}'"
            continue

        message = process(input_text)
        # if input_text has key words such as "exit", "quit", "goodbye", "bye" process Stops with Break.
        if input_text.lower() in ['exit', 'quit', 'bye', 'goodbye']:
            print('[Eliza]: ' + message)
            break


#####################################
#    Main text process stats here   #
#####################################
# Process function is where Eliza match key words using regular expression in Rules Dictionary (RULES.items)
def process(user_input):
    """Bot message processor

    This function will receive the user_input and will try to understand the input based on the RULES that were defined
    on the RULES Dictionary at the top of the application.

    - First it will preprocess by tokenizing and normalizing the input (remove punctuation, special characters) and
    lower the text input
    - With the normalized_user_input, then it will for each RULE in the RULES Dictionary try to match the regex
    on the RULE with the normalized_user_input and if there is a match will look for the last text on the regex group match
    and replace/format in the text with the placeholder {}.
    - Special Case:
        When the Rule is of Type 'name' we will store the information for later use.
        for all responses found in the RULES match output, we will try to replace the placeholder {{NAME}}
        with the value of USER_NAME global variable to represent person identification from the Bot.

    :param user_input:
    :return: sentence
    """
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


############################################################################
#    Bellow this point are mostly support functions for the main process   #
############################################################################

def is_valid(input_text):
    """Verify if input is valid to proceed to RULE parsing.
      This function using If statement to detect all non-alphabetical input content
      if the input is valid to proceed this method will return True otherwise False.
      if there is a single special character as a text this input is not valid.

    :param input_text:
    :return: Boolean
    """
    if input_text.strip(' ') == '':
        return True
    # check for only numbers and symbols:
    word_tokens = word_tokenize(input_text)
    for word in word_tokens:
        if word.isalpha():
            return True
    else:
        return False


# normalize_and_tokenize function tokenize text and set them in lowercase
def normalize_and_tokenize(text):
    """
    This function will Lower the text and call the word_tokenizer(text) to retrieve the tokenized lower case text
    :param text:
    :return: lowered tokenized text.
    """
    tokens = word_tokenize(text.lower())
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


def convert_response_as_text(tokens):
    """ Reponse Grammar perspective converter
    This will return a joined sentence from tokens while at the same time changing the response grammar perspective.
    :param tokens:
    :return: sentence
    """
    return " ".join(change_perspective(tokens))


def change_perspective(tokens):
    """ Change Text grammar point of view from user to Eliza BOT perspective.
    This function change perspective will use the dictionary RESPONSE_CONVERTERS and iterate through each item to
    replace texts from the Key to the value in order to change the user's perspective accordingly to the mapping provided.

    we ignore case for this comparison to make regex easier and more concise to write on the mapping.

    For example, if the user says: "i am crazy" the output should be "you are crazy"

    :param tokens:
    :return: grammar perspective user change.
    """
    for i, j in enumerate(tokens):
        for convert_from, convert_to in RESPONSE_CONVERTERS.items():
            tokens[i] = re.sub(convert_from, convert_to, tokens[i], flags=re.IGNORECASE)
    return tokens


# This indicates that the program is being executed from the command line
# and that the initial function to be called is main()
# and protects users from accidentally invoking the script when using as import
if __name__ == "__main__":
    main()
