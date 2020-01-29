from os import getenv
from flask import Flask, render_template
from .models import DB, User, Tweet
from .twitter import add_user_to_db


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ENV'] = getenv('ENV')
    DB.init_app(app)

    @app.route('/')
    def index():
        users = User.query.all()
        return render_template('base.html', title='Index Page', users=users)

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template('base.html', title="DB Reset!", users=[])

    @app.route('/user/<name>')
    def show_user_tweets(name):
        stmt = User.query.filter(User.name == name).first()
        if stmt is None:
            add_user_to_db(name)
        db_user = User.query.filter(User.name == name).first()
        db_user_id = db_user.id
        db_tweets = Tweet.query.filter(Tweet.user_id == db_user_id)
        return render_template('user.html', title=f'Tweets for @{name}',
                               name=name, tweets=db_tweets)

    return app
