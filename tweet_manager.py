import sys
import tweepy
import HTMLParser
import re
import itertools
import os.path
if not os.path.isfile('settings/default_secrets.py'):
    from settings.secrets import CONSUMER_TOKEN, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET
else:
    from settings.default_secrets import CONSUMER_TOKEN, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET
from settings.config import USER_IDS
from app import db, Tweets
import datetime


def authorize():
    try:
        auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
        api = tweepy.API(auth)
    except Exception as e:
        with open('logs/error.log', 'a+') as f:
            f.write('%s \n' % (e))
        return False
    return api


def clean_data(tweet):
    try:
        # avoid retweets
        if tweet.split()[0] == 'RT':
            return False
        # remove html tags
        html_parser = HTMLParser.HTMLParser()
        tweet = html_parser.unescape(tweet)
        # decode
        tweet = tweet.decode("utf8").encode('ascii', 'ignore')
        # convert lingos to words
        # TODO implement slang lookup
        #tweet = _slang_loopup(tweet)
        # standardize words
        tweet = ''.join(''.join(s)[:2] for _, s in itertools.groupby(tweet))
        # remove URLS, remove HTML tags
        emoticons_str = r"""
        (?:
             [:=;] # Eyes
             [oO\-]? # Nose (optional)
             [D\)\]\(\]/\\OpP] # Mouth
        )"""
        regex_str = [
            emoticons_str,
            r'<[^>]+>',  # HTML tags
            r'(?:\#+[\w_]+[\w\'_\-]*[\w_]+)',
            r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',
        ]

        tokens_re = re.compile(
            r'(' + '|'.join(regex_str) + ')', re.VERBOSE | re.IGNORECASE)
        words_to_remove = tokens_re.findall(tweet)
        # remove @ from mentions and replace underscores with non-spaces and
        # form the final tweet
        final_tweet = ' '.join(
            [word
             if word[0] != '@' else ''.join(word[1:].split('_')) + ', '
             for word in tweet.split()
             if word not in words_to_remove]
        )
    except:
        return False
    else:
        return final_tweet


def store(data):
    for user_id in USER_IDS:
        for tweet in data[user_id]:
            try:
                row = Tweets(
                    username=user_id,
                    created_on=tweet['created_on'],
                    tweet=tweet['text'],
                    tweet_id=tweet['tweet_id'],
                )
                db.session.add(row)
                db.session.commit()
            except Exception as e:
                with open('logs/error.log', 'a+') as f:
                    f.write('%s \n' % (e))


def get_latest_tweet_id(user_id):
    try:
        obj = Tweets.query.filter(Tweets.username == user_id).order_by(
            Tweets.tweet_id.desc()).first()
    except Exception as e:
        with open('logs/error.log', 'a+') as f:
            f.write('%s \n' % (e))
        return None
    else:
        return None if not obj else obj.tweet_id

if __name__ == '__main__':

    api = authorize()
    if not api:
        sys.exit()

    all_tweet_data = {}
    for user_id in USER_IDS:
        all_tweet_data[user_id] = []

        # GET THE LATEST STORED TWITTER ID
        latest_id = get_latest_tweet_id(user_id)
        try:
            tweets = api.user_timeline(id=user_id, since_id=latest_id)
        except Exception as e:
            with open('logs/error.log', 'a+') as f:
                f.write('%s \n' % (e))
            sys.exit()
        for tweet in tweets:
            tweet_data = {}
            tweet_data['tweet_id'] = tweet.id
            clean_tweet = clean_data(tweet.text)
            if not clean_tweet:
                continue
            tweet_data['text'] = clean_tweet
            tweet_data['created_on'] = tweet.created_at
            all_tweet_data[user_id].append(tweet_data)

        # store tweets in the database
    store(all_tweet_data)
