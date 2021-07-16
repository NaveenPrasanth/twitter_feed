from flask_sqlalchemy import SQLAlchemy
from main_app import FLASK_APP

FLASK_APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
FLASK_APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(FLASK_APP)


class Tweet(db.Model):
    __tablename__ = 'tweet'
    id = db.Column(db.String(80), primary_key=True)
    text = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.String(80), db.ForeignKey('user.user_id'), nullable=False)


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.String(80), nullable=False, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    latest_tweet_id = db.Column(db.String(80))


if __name__ == '__main__':
    db.create_all()
