from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from main_app import FLASK_APP
from flask_sqlalchemy import SQLAlchemy
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage

FLASK_APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
FLASK_APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(FLASK_APP)


class Tweet(db.Model):
    """
        Class to model Tweets
    """
    __tablename__ = 'tweet'
    id = db.Column(db.String(80), primary_key=True)
    text = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.String(80), db.ForeignKey('user.id'), nullable=False)


class User(UserMixin, db.Model):
    """
        Class to model the users. The newest tweet is held as reference to facilitate further pulls
    """
    __tablename__ = 'user'
    id = db.Column(db.String(80), nullable=False, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    latest_tweet_id = db.Column(db.String(80))


class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)





if __name__ == '__main__':
    db.create_all()
