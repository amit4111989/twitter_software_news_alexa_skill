
from app import db

class Tweets(db.Model):
    __tablename__='tweets'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    created_on = db.Column(db.DateTime())
    tweet = db.Column(db.Text())
    tweet_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    
    def serialize(self):
        """ Return data in serializable format """
        return { 'id': self.id , 'username': self.username, 'created_on':self.created_on.strftime("%Y-%m-%dT%H-%M-%S"), 'tweet':self.tweet}
     
    def __repr__(self):
        return '<%r - %r>' % (self.username, self.tweet)

class ReadFlag(db.Model):
    __tablename__='flags'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    tweet_id = db.Column(db.Integer)
    
    def __repr__(self):
        return '<%r>'%(self.timestamp)
