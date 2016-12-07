import os
import types
from dateutil import parser
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_ask import Ask, statement, question
# from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO
from migrate.versioning import api

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
    os.path.join(basedir, 'app2.db')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
ask = Ask(app, "/test_read")

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# import after declaring db
from models import Tweets, ReadFlag

# ROUTES/VIEWS


@app.route("/")
def test_read_page():
    return 'random message'

# BASIC APIS. NOT UPDATED


@app.route("/add", methods=['POST'])
def add_entry():
    tweet = Tweets(username=request.form['username'], tweet=request.form[
                   'tweet'], created_on=parser.parse(request.form['created_on']))
    db.session.add(tweet)
    try:
        db.session.commit()
        print 'Tweets added to Database'
    except Exception as e:
        raise Exception('%s' % (e))
    return "Tweet Added"


@app.route("/read", methods=['GET'])
def get_entries():
    return jsonify(json_list=[row.serialize() for row in Tweets.query.all()])


# ALEXA FUNCTIONS

def combine_all_tweets(data, new=False):
    tweet_collection = []
    tweet_count = 0
    for tweets in data:
        tweet_count += 1
        tweet_collection.append('Tweet number %d , <p>  ,' %
                                (tweet_count) + tweets.tweet)
    if not new:
        content = '<speak> There are %d old software feeds available right now <break time="1s"/>' % (
            len(data)
        )
    else:
        content = '<speak> There are %d new software feeds available right now <break time="1s"/>' % (
            len(data)
        )

    content += ' </p> <break time="1s"/>  ,'.join(tweet_collection)
    content += ' </p> </speak>'

    return content


@ask.intent("SoftwareIntent")
def software_skill():
    # TODO if no new tweets, ask if the user wants to hear old tweets starting

    all_tweets = Tweets.query.order_by(Tweets.tweet_id.desc()).all()

    if all_tweets:
        last_tweet_id = all_tweets[0].tweet_id
        try:
            last_read_tweet_id = ReadFlag.query.order_by(
                ReadFlag.timestamp.desc()).all()

        except Exception as e:
            with open('logs/error.log', 'a+') as f:
                f.write('%s \n' % (e))
            return statement('An error occurred. Please try asking again. Thank You')

        else:
            if last_read_tweet_id:
                last_read_tweet_id = last_read_tweet_id[0].tweet_id
                if last_tweet_id == last_read_tweet_id:
                    return question('There are no new tweets available. Would you like to hear old tweets starting with the most recent')
                else:
                    all_tweets = Tweets.query.filter(Tweets.tweet_id > last_read_tweet_id).order_by(
                        Tweets.tweet_id.desc()).all()

            content = combine_all_tweets(all_tweets, new=True)
            # TODO store timestamp with last read tweet id if all tweets are
            # read

            flag = ReadFlag(tweet_id=all_tweets[0].tweet_id)
            db.session.add(flag)
            db.session.commit()
            return statement(content)

    else:
        return statement('Sorry there are no tweets available. Have a nice day')


@ask.intent("YesIntent")
def read_random_tweets():
    all_tweets = Tweets.query.order_by(Tweets.tweet_id.desc()).all()
    content = combine_all_tweets(all_tweets)
    return statement(content)


@ask.intent("NoIntent")
def no_intent():
    bye_text = "Thank You. Have a nice day"
    return statement(bye_text)


if __name__ == '__main__':
    app.run(debug=True)
