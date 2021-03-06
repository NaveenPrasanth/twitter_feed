from flask_login import login_user
from database import *
from datetime import datetime
import tweet_service
from tweet_service import TweetServiceCallException
from sqlalchemy import desc
import requests
from loguru import logger

dict_filter = lambda x, y: dict([(i, x[i]) for i in x if i in set(y)])
keys_selected = ('text', 'created_at')


def init_db():
    db.create_all()


def create_user_if_none(username, user_id):
    """
        Create the user object in the db if not present
        :param username: twitter username for the user
        :param user_id: twitter user_id assigned to the user
        :return: None
    """
    try:
        user_obj = User.query.filter_by(id=user_id).first()
        if user_obj is None:
            user_obj = User(id=user_id, username=username)
            db.session.add(user_obj)
            db.session.commit()
        login_user(user_obj)

    except Exception as e:
        logger.error('Problem with database, cannot get or create user.')
        raise e


def get_persist_recent_tweets(user_id, twitter):
    """
        Gets the tweets from last fetched tweet as the reference and persists it in the db
        :param user_id: twitter user_id assigned to the user
        :param twitter: twitter oauth session object
        :return: None
    """
    try:
        user_obj = User.query.filter_by(id=user_id).first()
        recent_tweets = tweet_service.get_recent_tweets(user_id, twitter, user_obj.latest_tweet_id)
        if 'newest_id' in recent_tweets['meta']:  # else no new tweets
            user_obj.latest_tweet_id = recent_tweets['meta']['newest_id']
            for tweet in recent_tweets['data'][::-1]:
                created_at = datetime.strptime(tweet['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
                tweet_obj = Tweet(id=tweet['id'], created_at=created_at, text=tweet['text'], user_id=user_obj.id)
                db.session.add(tweet_obj)
            db.session.commit()
    except TweetServiceCallException as te:
        logger.error('Problem with twitter api calls: '+ str(te))
        raise te

    except Exception as e:
        logger.error('Problem with database queries.')
        raise e


def get_all_tweets(user_id):
    """
        Gets all the tweets for a particular db in the inserted order(implicit created order)
        :param user_id:
        :return:  return list of tweet dict {created_at, tweet_text}
    """
    try:
        return [dict_filter(t.__dict__, keys_selected) for t in Tweet.query.filter_by(user_id=user_id)]

    except Exception as e:
        logger.error('Problem with database queries.')
        raise e


def search_tweets(user_id, search_string):
    try:
        search_string = '%' + search_string + '%'
        return [dict_filter(t.__dict__, keys_selected) for t in
                Tweet.query.filter_by(user_id=user_id).filter(Tweet.text.ilike(search_string)).all()]

    except Exception as e:
        logger.error('Problem with database queries.')
        raise e


def filter_sort_tweets(user_id, from_date, to_date, sort_order):

    try:
        if from_date == '':
            from_date = datetime.min
        else:
            from_date = datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')

        if to_date == '':
            to_date = datetime.now()
        else:
            to_date = datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S')

        filtered = Tweet.query.filter_by(user_id=user_id).filter(Tweet.created_at.between(from_date, to_date))

        return [dict_filter(t.__dict__, keys_selected) for t in __sort_tweets(filtered, sort_order)]

    except ValueError as e:
        logger.error('Value error for dates')
        raise e

    except Exception as e:
        logger.error('Problem with database queries.')
        raise e


def __sort_tweets(objects, sort_order):
    if sort_order == 'desc':
        return objects.order_by(desc(Tweet.created_at)).all()
    elif sort_order == 'asc':
        return objects.order_by(Tweet.created_at).all()
    else:
        raise ValueError('Invalid sort type')


def sync_tweets_with_db():
    all_users = User.query.all()
    for user in all_users:
        get_persist_recent_tweets(user.id, requests)
