from flask import Blueprint, render_template, jsonify
from tweet_app.models import Users, parse_records

main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/')
def index():
    return render_template("index.html")

# html에서 사용하는 형식 
# 사전형으로 사용할때 사용.
@main_routes.route('/user.json')
def json_data():
    raw_data = Users.query.all()
    parsed_data = parse_records(raw_data)
    
    return jsonify(parsed_data)