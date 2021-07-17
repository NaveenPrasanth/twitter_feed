from main_app import FLASK_APP


def get_user_id_from_username(username, twitter):
    """
        Gets twitter assigned user_id from username. API call
        :param username: twitter username
        :param twitter: twitter oauth session object
        :return: twitter user_id
    """
    return twitter.get("https://api.twitter.com/2/users/by/username/"+username).json()['data']['id']


def get_recent_tweets(user_id, twitter, since_id):
    """
        Gets either the recent 100 tweets for a user_id or less based on the tweets already pulled. you can only pull
         the recent 100 tweets because of API constraints.
        :param user_id: twitter user_id
        :param twitter: twitter oauth session object
        :param since_id: the last tweet id that is fetched.
        :return: list of latest tweets in reverse chronological order
    """
    max_results = '&max_results=100'
    if since_id is not None:
        since_id = '&since_id='+since_id
    else:
        since_id = ''
    return twitter.get("https://api.twitter.com/2/users/"+user_id+"/tweets?tweet.fields=created_at,id,text"+since_id+max_results,
                       headers={"Authorization":"Bearer "+FLASK_APP.config['BEARER_TOKEN']}).json()
