import os
import types
from dateutil import parser
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_ask import Ask, statement, question
#from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO
from migrate.versioning import api

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
    os.path.join(basedir, 'app2.db')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
ask = Ask(app, "/test_read")

db = SQLAlchemy(app)
migrate = Migrate(app,db)

# import after declaring db
from models import Tweets

# ROUTES/VIEWS

@app.route("/")
def test_read_page():
    return 'random message'


@app.route("/add", methods=['POST'])
def add_entry():
    tweet = Tweets(username=request.form['username'], tweet=request.form['tweet'], created_on=parser.parse(request.form['created_on']))
    db.session.add(tweet)
    try:
        db.session.commit()
        print 'Tweets added to Database'
    except Exception as e:
        raise Exception('%s'%(e))
    return "Tweet Added"

@app.route("/read", methods=['GET'])
def get_entries():
    return jsonify(json_list=[row.serialize() for row in Tweets.query.all()])
    

# ALEXA FUNCTIONS

@ask.launch
def start_skill():
    welcome_message = 'Hello there, would you like to start this random skill'
    return question(welcome_message)


@ask.intent("YesIntent")
def read_random_tweets():
    tweets = get_tweets()
    tweet_msg = 'Our selection of random tweets are %s' % (tweets)
    return statement(tweet_msg)


@ask.intent("NoIntent")
def no_intent():
    bye_text = "Then why don't you fuck off man"
    return statement(bye_text)


def get_tweets():
    statement = "To get your whore name append your first name to your last name, because you are a whore you stinking bitch"
    return statement

if __name__ == '__main__':
    app.run(debug=True)
