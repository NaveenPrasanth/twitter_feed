from flask import Flask, url_for, Response
from flask import request, redirect
from flask import render_template
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
import tweet_service

FLASK_APP = Flask(__name__)

# read api keys from config and set to app
FLASK_APP.config.from_pyfile('./config/config.txt')
FLASK_APP.secret_key = FLASK_APP.config['APP_KEY']

# pass api keys to flask dance blueprints and register with app
blueprint = make_twitter_blueprint(
    api_key=FLASK_APP.config['API_KEY'],
    api_secret=FLASK_APP.config['API_SECRET_KEY'],
)
FLASK_APP.register_blueprint(blueprint, url_prefix="/login")

import middleware


@FLASK_APP.route('/')
def twitter_sign_in():
    """
        API to start twitter authentication and redirect to home page
        :return: redirect to home page
    """
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))
    else:
        return redirect(url_for('get_landing_page'))


@FLASK_APP.route('/home')
def get_landing_page():
    """
        API to get, persist and display user tweets
        :return: renders a webpage with list of user tweets
    """
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))

    resp = twitter.get("account/settings.json")
    assert resp.ok
    username = resp.json()["screen_name"]
    user_id = tweet_service.get_user_id_from_username(username, twitter)
    middleware.create_user_if_none(username, user_id)
    middleware.get_persist_recent_tweets(user_id, twitter)
    tweets_list = middleware.get_all_tweets(user_id)
    return render_template('index.html', name=resp.json()["screen_name"], tweets_list=tweets_list)


if __name__ == '__main__':
    FLASK_APP.run()
