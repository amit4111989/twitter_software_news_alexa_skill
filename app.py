from flask import Flask
from flask_ask import Ask, statement, question

app = Flask(__name__)
ask = Ask(app, "/test_read")

@app.route("/")
def test_read_page():
    return 'random message'

@ask.launch
def start_skill():
    welcome_message = 'Hello there, would you like to start this random skill'
    return question(welcome_message)

@ask.intent("YesIntent")
def read_random_tweets():
    tweets = get_tweets()
    tweet_msg = 'Our selection of random tweets are %s'%(tweets)
    return statement(tweet_msg)

@ask.intent("NoIntent")
def no_intent():
    bye_text = "Then why don't you fuck off man"
    return statement(bye_text)

def get_tweets():
    statement = "To get your whore name append your first name to your last name, because you are a whore you stinking bitch"
    return statement

if __name__=='__main__':
    app.run(debug=True)


