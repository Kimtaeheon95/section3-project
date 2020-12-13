from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()#session_options={"autoflush": False}
migrate = Migrate()


class Users(db.Model):
    __tablename__ = "Users"
    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String)
    full_name = db.Column(db.String)
    followers = db.Column(db.Integer)

    def __repr__(self):
        return f"< User {self.id} {self.username} >"


class Tweet(db.Model):
    __tablename__ = "Tweet"
    id = db.Column(db.BigInteger, primary_key=True)
    text = db.Column(db.String)
    embedding = db.Column(db.PickleType)
    user_id = db.Column(db.BigInteger, db.ForeignKey("Users.id"))

    user = db.relationship("Users", foreign_keys = user_id, backref=db.backref('tweets', lazy=True))

    def __repr__(self):
        return f"<Tweet {self.id} {self.text}>"

    

def parse_records(db_records):
    parsed_list = []
    for record in db_records:
        parsed_record = record.__dict__
        print(parsed_record)
        del parsed_record["_sa_instance_state"]
        parsed_list.append(parsed_record)
    return parsed_list

