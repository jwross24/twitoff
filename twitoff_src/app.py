"""Main application and routing logic for TwitOff."""
from os import getenv
from flask import Flask, render_template, request
from .models import DB, User
from .predict import predict_user
from .twitter import add_or_update_user, update_all_users


def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    # Add config for database
    app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL')

    # Stop tracking modifications on SQLAlchemy config
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Let the database know about the app
    DB.init_app(app)

    # Initialize recent comparisons in the cache
    comparisons = []

    @app.route('/')
    def root():
        DB.create_all()
        users = User.query.all()
        message = 'Home'
        return render_template('base.html', title=message, message=message,
                               users=users, comparisons=comparisons)

    @app.route('/user', methods=['POST'])
    @app.route('/user/<name>', methods=['GET'])
    def user(name=None, message=''):
        name = name or request.values['username']
        try:
            if request.method == "POST":
                add_or_update_user(name)
                message = f'User @{name} successfully added!'
            tweets = User.query.filter(User.name == name).one().tweets
        except Exception as e:
            message = f'Error while trying to add user @{name}: {e}'
            tweets = []
        return render_template('user.html', title=name, message=message,
                               tweets=tweets)

    @app.route('/compare', methods=['POST'])
    def compare(message=''):
        users = User.query.all()
        user1, user2 = sorted([request.values['user1'],
                               request.values['user2']])
        if user1 == user2:
            message = "Cannot compare a user to themselves!"
        elif request.values['tweet_text'] == '':
            message = "Cannot compare an empty Tweet!"
            return render_template('base.html', title=message, message=message,
                                   users=users, comparisons=comparisons)
        else:
            prediction = predict_user(user1, user2,
                                      request.values['tweet_text'])
            message = (
                f"\"{request.values['tweet_text']}\" is more likely to be "
                f"said by @{user1 if prediction else user2} than "
                f"@{user2 if prediction else user1}."
            )
            comparisons.append([user1, user2])
        return render_template('prediction.html', title='Prediction',
                               message=message)

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        message = "Reset database!"
        comparisons.clear()
        return render_template('base.html', title=message, message=message,
                               users=[], comparisons=comparisons)

    @app.route('/update')
    def update():
        try:
            update_all_users()
            message = "Cache cleared and all Tweets updated!"
            comparisons.clear()
        except Exception as e:
            message = f"Error while updating Tweets: {e}"
        return render_template('base.html', title=message, message=message,
                               users=User.query.all(), comparisons=comparisons)

    return app
