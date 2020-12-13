import numpy as np
import pickle
import os
import tweepy
from flask import Blueprint, render_template, request
from tweet_app.models import db, Users, Tweet
from embedding_as_service_client import EmbeddingClient
from sklearn.linear_model import LogisticRegression
from dotenv import load_dotenv

load_dotenv()

API_KEY=os.getenv('API_KEY')
API_KEY_SECRET=os.getenv('API_KEY_SECRET')
ACCESS_TOKEN=os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET=os.getenv('ACCESS_TOKEN_SECRET')

# tweety와 연결
auth=tweepy.OAuthHandler(API_KEY,API_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN,ACCESS_TOKEN_SECRET)

api=tweepy.API(auth)


# 모델파일 저장경로
FILEPATH = "./model.pkl"

en = EmbeddingClient(host = '54.180.124.154', port = 8989)
tweet_routes = Blueprint('tweet_routes', __name__)


@tweet_routes.route('/users/')
def users():
    data = Users.query.all()
    return render_template("user.html", data = data)


@tweet_routes.route('/add', methods = ["GET", "POST"])
def add():
    if request.method == "POST":
        result = request.form # form 에 작성된 모든 값을 가져온다.
        ## Tweepy
        new = api.get_user(screen_name = result['username'])
        tweets = api.user_timeline(screen_name = result['username'], tweet_mode = "extend")

        # Insert data into Users Table
        # 이제 model에 있는 User라는 테이블에, 트위터에서 불러온 정보들을 저장. 
        user = Users.query.get(new.id) or Users(id = new.id)# Users()라는 클래스를 불러오고
        user.username = new.screen_name.casefold()# 소문자화 시키는 명령어 >> .casefold()
        user.full_name = new.name
        user.followers = new.followers_count
        # user.location = new.location
        
        db.session.add(user) # 데이터베이스에 user = Users()에 저장하고

        for tw in tweets:
            tweet = Tweet.query.get(tw.id) or Tweet(id = tw.id)
            tweet.text = tw.text
            tweet.embedding = en.encode(texts = [tw.text])
            print(tw.user.id)
            tweet.user_id = tw.user.id
            # breakpoint()
            db.session.add(tweet)

        db.session.commit()

    return render_template('add.html')


@tweet_routes.route('/get', methods = ["GET", "POST"])
def index():
    tweet_data = None
    if request.method == "POST":

        twit_user = request.form
        input_name = twit_user['see_tweets']

        user_info = Users.query.filter_by(username = input_name).one()
        user_id = user_info.__dict__['id']

        tweet_data = Tweet.query.filter_by(user_id = user_id)

        # breakpoint

    return render_template("get.html", data = tweet_data)


@tweet_routes.route('/delete', methods=["GET", "POST"])
def delete():
    if request.method == "POST":

        twit_user = request.form # html의 from을 참조한다.
        input_name = twit_user['delete_user']


        user_info = Users.query.filter_by(username = input_name).one()
        user_id = user_info.__dict__['id']

        Tweet.query.filter_by(user_id = user_id).delete()
        Users.query.filter_by(username = input_name).delete()

        db.session.commit()

    data = Users.query.all()
    return render_template("delete.html", data=data)

@tweet_routes.route('/update', methods = ["GET", "POST"])
def update():
    if request.method == "POST":

        update_user = request.form
        old_name = update_user['input_full_old']
        new_name = update_user['input_full_new']
        
        Users.query.filter_by(username = old_name).update({'username': new_name})
        db.session.commit()
    
    data = Users.query.all()
    
    return render_template("update.html", data=data)


def append_to_with_label(to_arr, from_arr, label_arr, label):
    """
    from_arr 리스트에 있는 항목들을 to_arr 리스트에 append 하고
    레이블도 같이 추가해주는 함수입니다.
    """

    for item in from_arr:
        to_arr.append(item)
        label_arr.append(label)

@tweet_routes.route('/compare', methods = ["GET", "POST"])
def compare():
    statement = ''
    if request.method == "POST":
        print(dict(request.form))
        X = []
        y = []

        comparing = request.form
        user1 = comparing['user1']
        user2 = comparing['user2']
        tweet_to_compare = comparing['tweet_to_predict']

        user1_tweet_list = Users.query.filter_by(username=user1).one().tweets
        user1_id = Users.query.filter_by(username=user1).one().id
        for tweet in user1_tweet_list:
            X.append(tweet.embedding)
            y.append(user1_id)

        user2_tweet_list = Users.query.filter_by(username=user2).one().tweets
        user2_id = Users.query.filter_by(username=user2).one().id
        for tweet in user2_tweet_list:
            X.append(tweet.embedding)
            y.append(user2_id)

        text_array = np.array(X)

        nsamples, nx, ny = text_array.shape

        text_2d = text_array.reshape(nsamples, nx * ny)

        classifier = LogisticRegression()
        classifier.fit(text_2d, y)

        em_pred_val = en.encode(texts=[tweet_to_compare])

        pred_result = classifier.predict(em_pred_val)

        user_info = Users.query.filter_by(id=int(pred_result)).one()
        user_name = user_info.__dict__['username']

        statement = f"Between '{user1}' and '{user2}', who is more likely to tweet '{tweet_to_compare}' is '{user_name}'. "
        
    data = Users.query.all()
    return render_template("compare.html", data=data, statement=statement)
