import middleware
from _pytest.monkeypatch import MonkeyPatch
import pytest
from database import *
from datetime import datetime
import tweet_service
import requests

# fixtures setup
monkey_patch = MonkeyPatch()


@pytest.fixture(scope='module')
def db_init():
    db.create_all()
    user_obj = User(id='1231123', username='test', latest_tweet_id='123213')
    tweet_obj = Tweet(id='1283712', created_at=datetime.strptime('2019-09-08 08:09:27', '%Y-%m-%d %H:%M:%S'),
                      text='dummy', user_id='2121321')
    db.session.add(tweet_obj)
    db.session.add(user_obj)
    db.session.commit()
    yield db
    db.drop_all()


@pytest.mark.parametrize("recent_tweet", [({'meta': {'newest_id': '12312312'}, 'data': [{'id':'12321', 'created_at': '2018-08-01T09:56:34.000Z', 'text':'this is a tweet'}]}),
                                                        ({'meta': {}})])
def test_get_persist_recent_tweets(db_init, recent_tweet):
    monkey_patch.setattr(tweet_service, 'get_recent_tweets', lambda x,y,z: recent_tweet)
    response = middleware.get_persist_recent_tweets('1231123', twitter=requests)
    # asserts the methods executed without exception and returned
    assert response is None


@pytest.mark.parametrize("user_id, from_date, to_date, sort_order, is_exception", [('1283712', '', '', '', True),
                                                                                   ('1283712', '2019-09-08 08:09:27',
                                                                                    '2019-09-08 08:09:27', 'asc',
                                                                                    False),
                                                                                   ('1283712', '2019-09-08 08:09:27',
                                                                                    '2019-09-08 08:09:27', 'desc',
                                                                                    False),
                                                                                   ('1283712', '2019/09/08 08:09:27',
                                                                                    '2019-09-08 08:09:27', 'desc',
                                                                                    True),
                                                                                   ])
def test_filter_sort_tweets(db_init, user_id, from_date, to_date, sort_order, is_exception):
    if not is_exception:
        response = middleware.filter_sort_tweets(user_id, from_date, to_date, sort_order)
        assert response == []

    else:
        with pytest.raises(Exception):
            middleware.filter_sort_tweets(user_id, from_date, to_date, sort_order)
