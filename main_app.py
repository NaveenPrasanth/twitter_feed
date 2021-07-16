from flask import Flask, url_for, Response
from flask import request, redirect
from flask import render_template, jsonify
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
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

    username = twitter.token["screen_name"]
    user_id = twitter.token['user_id']
    middleware.create_user_if_none(username, user_id)
    middleware.get_persist_recent_tweets(user_id, twitter)
    return render_template('index.html', name=username)


@FLASK_APP.route('/all_tweets')
def get_all_tweets():
    """
        API to get, persist and display user tweets
        :return: renders a webpage with list of user tweets
    """
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))

    user_id = twitter.token['user_id']
    tweets_list = middleware.get_all_tweets(user_id)
    return jsonify(tweets_list)


@FLASK_APP.route('/search/<search_string>')
def search_tweets(search_string):
    """
        API to search for a substring in user tweets
        :return: renders a webpage with list of user tweets based on search string
    """
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))

    user_id = twitter.token['user_id']
    tweets_list = middleware.search_tweets(user_id, search_string)
    return jsonify(tweets_list)


if __name__ == '__main__':
    FLASK_APP.run()
