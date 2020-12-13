import os
from flask import Flask
from tweet_app.routes import main_routes, tweet_routes
from flask import Blueprint, render_template, request
from tweet_app.models import db, Users, Tweet, migrate
from dotenv import load_dotenv
load_dotenv()


# "postgres://dycbejwq:9KNAQNHT9HCLFwDKm_IJOGdGwRNpkF5P@arjuna.db.elephantsql.com:5432/dycbejwq"
DATABASE_URI = "sqlite:///twit.sqlite3"

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(main_routes.main_routes)
    app.register_blueprint(tweet_routes.tweet_routes)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)