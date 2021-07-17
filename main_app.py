from flask import Flask, url_for, Response
from flask import request, redirect
from flask import render_template, jsonify
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask_login import LoginManager

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
login_manager = LoginManager()
login_manager.init_app(FLASK_APP)
import middleware
from database import User


@FLASK_APP.cli.command()
def sync_tweets_with_db():
    """
        Sync tweets with db
    :return:
    """
    middleware.sync_tweets_with_db(blueprint, twitter)


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


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
    middleware.create_user_if_none(username, user_id, blueprint)
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
    user_id = twitter.token['user_id']
    tweets_list = middleware.search_tweets(user_id, search_string)
    return jsonify(tweets_list)


@FLASK_APP.route('/filter/<from_date>/<to_date>/<sort_order>')
def filter_sort_tweets(from_date, to_date, sort_order):
    """
        API to search for a substring in user tweets
        :return: renders a webpage with list of user tweets based on search string
    """

    user_id = twitter.token['user_id']
    tweets_list = middleware.filter_sort_tweets(user_id, from_date, to_date, sort_order)
    return jsonify(tweets_list)


if __name__ == '__main__':
    FLASK_APP.run()
