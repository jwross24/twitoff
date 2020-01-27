from flask import Flask, render_template


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return "Index Page"

    @app.route('/hello')
    def hello():
        return render_template('base.html', title='hello')

    return app
