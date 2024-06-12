from flask import Blueprint, request,jsonify, make_response,session
external_route = Blueprint('external_route', __name__)
from utils.JwtToken import validate_token_admin,validate_apiKey
import threading
from services.chatbot_services import train_bot_text
from services.api_services import add_chatbot_text_bykey


@external_route.route('/api/v1/external/addChatbotTextBykey', methods=['GET', 'POST'])
@validate_apiKey
def addChatbotTextBykey():
    try:
        data = request.get_json()
        response=add_chatbot_text_bykey(data)    
        if(response['status']==True):
            bg_thread = threading.Thread(target=train_bot_text, args=(response['res_data'],response['update_id']))
            bg_thread.daemon = True  # Allow the thread to exit when the main process exits
            bg_thread.start()
        return response
    except Exception as e:
        print(e)
        return make_response({'message': str(e)}, 404) 
