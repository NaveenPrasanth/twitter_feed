from flask import Flask, url_for, Response
from flask import request, redirect
from flask import render_template, jsonify
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask_login import LoginManager
from loguru import logger
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
#http://52.66.208.89/login/twitter/authorized
logger.add("app_{time}.log")

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
from database import *


def sync_tweets_with_db():
    """
        Sync tweets with db
    :return:
    """
    try:
        logger.info("Scheduled tweet pull initiated")
        middleware.sync_tweets_with_db()
    except Exception as e:
        logger.error("Exception running offline sync: " + str(e))


scheduler = BackgroundScheduler()
scheduler.add_job(func=sync_tweets_with_db, trigger="interval", seconds=300)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


@FLASK_APP.route('/')
def twitter_sign_in():
    """
        API to start twitter authentication and redirect to home page
        :return: redirect to home page
    """
    middleware.init_db()
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
    middleware.init_db()
    if not twitter.authorized:
        return redirect(url_for("twitter_sign_in"))
    username = twitter.token["screen_name"]
    logger.info('Fetching Tweets for user: '+str(username))
    user_id = twitter.token['user_id']
    try:
        middleware.create_user_if_none(username, user_id)
        middleware.get_persist_recent_tweets(user_id, twitter)
        return render_template('index.html', name=username)
    except Exception as e:
        logger.error('Exception in get_landing_page: '+str(e))
        return render_template('error.html')


@FLASK_APP.route('/all_tweets')
def get_all_tweets():
    """
        API to get, persist and display user tweets
        :return: renders a webpage with list of user tweets
    """
    if not twitter.authorized:
        return redirect(url_for("twitter_sign_in"))
    try:
        user_id = twitter.token['user_id']
        tweets_list = middleware.get_all_tweets(user_id)
        return jsonify(tweets_list)
    except Exception as e:
        logger.error('Exception in get_all_tweets: ' + str(e))
        return jsonify({'is_success': False})


@FLASK_APP.route('/search/<search_string>')
def search_tweets(search_string):
    """
        API to search for a substring in user tweets
        :return: renders a webpage with list of user tweets based on search string
    """
    try:
        user_id = twitter.token['user_id']
        tweets_list = middleware.search_tweets(user_id, search_string)
        return jsonify(tweets_list)
    except Exception as e:
        logger.error('Exception in get_all_tweets: ' + str(e))
        return jsonify({'is_success': False})


@FLASK_APP.route('/filter')
def filter_sort_tweets():
    """
        API to search for a substring in user tweets
        :return: renders a webpage with list of user tweets based on search string
    """
    try:
        from_date = request.args.get("from_date")
        to_date = request.args.get("to_date")
        sort_order = request.args.get("sort_order")
        user_id = twitter.token['user_id']
        tweets_list = middleware.filter_sort_tweets(user_id, from_date, to_date, sort_order)
        return jsonify(tweets_list)
    except Exception as e:
        logger.error('Exception in get_all_tweets: ' + str(e))
        return jsonify({'is_success': False})


if __name__ == '__main__':
    FLASK_APP.run()
