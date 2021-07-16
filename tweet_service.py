
def get_user_id_from_username(username, twitter):
    return twitter.get("https://api.twitter.com/2/users/by/username/"+username).json()['data']['id']


def get_recent_tweets(user_id, twitter, since_id):
    if since_id is not None:
        since_id = '&since_id='+since_id
    else:
        since_id = ''
    return twitter.get("https://api.twitter.com/2/users/"+user_id+"/tweets?tweet.fields=created_at,id,text"+since_id).json()