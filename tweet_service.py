from main_app import FLASK_APP
from loguru import logger


class TweetServiceCallException(Exception):
    pass


def get_user_id_from_username(username, twitter):
    """
        Gets twitter assigned user_id from username. API call
        :param username: twitter username
        :param twitter: twitter oauth session object
        :return: twitter user_id
    """
    try:
        logger.info('Getting user_id from username using: '+ username)
        response = twitter.get("https://api.twitter.com/2/users/by/username/" + username)
        if response.status_code == 200:
            return response.json()['data']['id']
        else:
            logger.error('Request did not succeed.')
            raise TweetServiceCallException("Unable to make request with url: "+ "https://api.twitter.com/2/users/by/username/" + username)

    except TweetServiceCallException as tsce:
        raise tsce

    except Exception as e:
        raise e


def get_recent_tweets(user_id, twitter, since_id):
    """
        Gets either the recent 100 tweets for a user_id or less based on the tweets already pulled. you can only pull
         the recent 100 tweets because of API constraints.
        :param user_id: twitter user_id
        :param twitter: twitter oauth session object
        :param since_id: the last tweet id that is fetched.
        :return: list of latest tweets in reverse chronological order
    """
    try:
        max_results = '&max_results=100'
        if since_id is not None:
            since_id = '&since_id='+since_id
        else:
            since_id = ''
        logger.info('Getting recent tweets for user_id: ' + user_id)
        response = twitter.get("https://api.twitter.com/2/users/"+user_id+"/tweets?tweet.fields=created_at,id,text"+since_id+max_results,
                           headers={"Authorization":"Bearer "+FLASK_APP.config['BEARER_TOKEN']})
        if response.status_code == 200:
            return response.json()
        else:
            logger.info('Request did not succeed.')
            raise TweetServiceCallException("Unable to make request with url: "+ "https://api.twitter.com/2/users/"+user_id+"/tweets?tweet.fields=created_at,id,text"+since_id+max_results)

    except TweetServiceCallException as tsce:
        raise tsce

    except Exception as e:
        raise e
