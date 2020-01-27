import uuid
from flask import Flask, render_template
from .models import DB, User, Tweet


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_db.sqlite'
    DB.init_app(app)

    @app.route('/')
    def index():
        rand_name = str(uuid.uuid4())
        rand_u = User(name=rand_name)

        for i in range(3):
            new_tweet = Tweet(text=f'Tweet #{i}')
            rand_u.tweets.append(new_tweet)

        DB.session.add(rand_u)
        DB.session.commit()
        return "Index Page"

    @app.route('/hello')
    def hello():
        return render_template('base.html', title='hello')

    return app
