from os import getenv
from flask import Flask, render_template
from .models import DB, User


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

    return app
