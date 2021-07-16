from database import *
from datetime import datetime


def create_user_if_none(username, user_id):
    user_obj = User.query.filter_by(user_id=user_id).first()
    if user_obj is None:
        user_obj = User(user_id=user_id, username=username)
        db.session.add(user_obj)
        db.session.commit()
    return user_obj


def persist_recent_tweets(recent_tweets, user_id):
    user_obj = User.query.filter_by(user_id=user_id).first()
    user_obj.latest_tweet_id = recent_tweets['meta']['newest_id']
    for tweet in recent_tweets['data']:
        created_at = datetime.strptime(tweet['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
        tweet_obj = Tweet(id=tweet['id'], created_at=created_at, text=tweet['text'], user_id=user_obj.user_id)
        db.session.add(tweet_obj)
    db.session.commit()


def get_all_tweets(user_id):
    return [t.__dict__ for t in Tweet.query.filter_by(user_id=user_id)]



