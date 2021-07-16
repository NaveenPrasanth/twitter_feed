from flask import Flask, url_for, Response
from flask import request, redirect
from flask import render_template
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter

FLASK_APP = Flask(__name__)

'''
    Read keys from config rather than hardcoding 
'''
FLASK_APP.config.from_pyfile('./config/config.txt')


FLASK_APP.secret_key = FLASK_APP.config['APP_KEY']
blueprint = make_twitter_blueprint(
    api_key=FLASK_APP.config['API_KEY'],
    api_secret=FLASK_APP.config['API_SECRET_KEY'],
)
FLASK_APP.register_blueprint(blueprint, url_prefix="/login")


@FLASK_APP.route('/')
def twitter_sign_in():
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))
    resp = twitter.get("account/settings.json")
    assert resp.ok
    return "You are @{screen_name} on Twitter".format(screen_name=resp.json()["screen_name"])


if __name__ == '__main__':
    FLASK_APP.run()
