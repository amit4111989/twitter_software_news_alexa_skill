from flask import Flask, request, session, g, redirect, url_for, abort
import sqlite3
import os
from flask_ask import Ask, statement, question

app = Flask(__name__)
ask = Ask(app, "/test_read")


app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'test_skill.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('TESTSKILL_SETTINGS', silent=True)

# DATABASE CONNECTION

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

# ROUTES

@app.route("/")
def test_read_page():
    return 'random message'

@app.route("/add", methods=['POST'])
def add_entry():
    db = get_db()
    db.execute('insert into tweets (username, created_on, tweet) values (?, ?, ?)',
                 [request.form['username'], request.form['create_on'], request.form['tweet']])
    db.commit()
    print 'Tweets added to Database'
    return True

#VIEWS


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


