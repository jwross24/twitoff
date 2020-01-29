from os import getenv
import uuid
from flask import Flask, render_template
from .models import DB, User, Tweet


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

    @app.route('/hello')
    def hello():
        rand_name = str(uuid.uuid4())
        rand_u = User(name=rand_name)

        for i in range(3):
            new_tweet = Tweet(text=f'Tweet #{i}')
            rand_u.tweets.append(new_tweet)

        DB.session.add(rand_u)
        DB.session.commit()

        return render_template('base.html', title='hello')

    return app
