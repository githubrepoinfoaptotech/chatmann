from flask import Blueprint, request,jsonify, make_response,session
from services.facebookChat_services import recive_facebook_message
facebook_route = Blueprint('facebook_route', __name__)
from utils.JwtToken import validate_token_admin,validate_apiKey



@facebook_route.route('/api/v1/facebook/reciveFacebookMessage', methods=['GET', 'POST'])
# @validate_apiKey
def reciveFacebookMessage():
    data = request.get_json()
    return recive_facebook_message(data)