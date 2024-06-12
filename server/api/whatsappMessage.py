from flask import Blueprint, request,jsonify, make_response,session
from services.whatsAppChat_services import recive_whatsapp_message
whatsapp_route = Blueprint('whatsapp_route', __name__)
from utils.JwtToken import validate_token_admin,validate_apiKey


@whatsapp_route.route('/api/v1/whatsapp/reciveWhatsappMessage', methods=['GET', 'POST'])
# @validate_apiKey
def reciveWhatsappMessage():
    data = request.get_json()
    return recive_whatsapp_message(data)