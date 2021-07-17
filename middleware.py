from flask_login import login_user
from flask_login import current_user
from database import *
from datetime import datetime
import tweet_service
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage

dict_filter = lambda x, y: dict([(i, x[i]) for i in x if i in set(y)])
keys_selected = ('text', 'created_at')


def create_user_if_none(username, user_id, blueprint):
    """
        Create the user object in the db if not present
        :param username: twitter username for the user
        :param user_id: twitter user_id assigned to the user
        :return: None
    """
    user_obj = User.query.filter_by(id=user_id).first()
    if user_obj is None:
        user_obj = User(id=user_id, username=username)
        db.session.add(user_obj)
        db.session.commit()
    login_user(user_obj)
    blueprint.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)


def get_persist_recent_tweets(user_id, twitter):
    """
        Gets the tweets from last fetched tweet as the reference and persists it in the db
        :param user_id: twitter user_id assigned to the user
        :param twitter: twitter oauth session object
        :return: None
    """
    user_obj = User.query.filter_by(id=user_id).first()
    recent_tweets = tweet_service.get_recent_tweets(user_id, twitter, user_obj.latest_tweet_id)
    if 'newest_id' in recent_tweets['meta']:  # else no new tweets
        user_obj.latest_tweet_id = recent_tweets['meta']['newest_id']
        for tweet in recent_tweets['data'][::-1]:
            created_at = datetime.strptime(tweet['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
            tweet_obj = Tweet(id=tweet['id'], created_at=created_at, text=tweet['text'], user_id=user_obj.id)
            db.session.add(tweet_obj)
        db.session.commit()


def get_all_tweets(user_id):
    """
        Gets all the tweets for a particular db in the inserted order(implicit created order)
        :param user_id:
        :return:  return list of tweet dict {created_at, tweet_text}
    """
    return [dict_filter(t.__dict__, keys_selected) for t in Tweet.query.filter_by(user_id=user_id)]


def search_tweets(user_id, search_string):
    search_string = '%'+search_string+'%'
    return [dict_filter(t.__dict__, keys_selected) for t in Tweet.query.filter_by(user_id=user_id).filter(Tweet.text.ilike(search_string)).all()]


def sync_tweets_with_db(blueprint, twitter):
    all_users = User.query.all()
    get_persist_recent_tweets(all_users[0].id, twitter)
