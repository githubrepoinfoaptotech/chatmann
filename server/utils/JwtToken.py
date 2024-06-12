import jwt
import os
from flask import make_response, request,session
import datetime
from model.chatbot import chatBots
def generate_token(payload, secret):
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=24)

    # Add the 'exp' claim to the payload
    payload['exp'] = expiration_time

    # Encode the payload and create the JWT token
    token_body = jwt.encode(payload, secret, algorithm="HS256")

    # Construct the complete token 
    token = "Bearer " + token_body

    return token

def validate_token_admin(func):
    secret = "qwertyuioplkmjnha5526735gbsgsg"
    def wrapper(*args, **kwargs):
        try:
            token = request.headers['Authorization']
            myPayload=token.split(" ")
        except Exception as e:
            return make_response({"message": "Token not provided"}, 403)
        
        try:
            payloads=jwt.decode(myPayload[1], secret, algorithms=["HS256"])
            print(payloads)
            if(payloads['role']=="ADMIN" or payloads['role']=="SUPERADMIN"):
                session['user_id'] = payloads['user_id']
                return func(*args, **kwargs)
            else:
                return make_response({"message": "Invalid User","status":False}) 
        except Exception as e: 
            print(e)
            return make_response({"message": "Invalid token provided","status":False})   
    wrapper.__name__ = func.__name__
    return wrapper
def validate_token_superadmin(func):
    secret = "qwertyuioplkmjnha5526735gbsgsg"
    def wrapper(*args, **kwargs):
        try:
            token = request.headers['Authorization']
            myPayload=token.split(" ")
        except Exception as e:
            return make_response({"message": "Token not provided"}, 403)
        
        try:
            payloads=jwt.decode(myPayload[1], secret, algorithms=["HS256"])
            print(payloads)
            if(payloads['role']=="SUPERADMIN"):
                session['user_id'] = payloads['user_id']
                return func(*args, **kwargs)
            else:
                return make_response({"message": "Invalid User","status":False}) 
        except Exception as e: 
            print(e)
            return make_response({"message": "Invalid token provided","status":False})   
    wrapper.__name__ = func.__name__
    return wrapper
def validate_apiKey(func):
    def wrapper(*args, **kwargs):
        try:
            key = request.headers['API-Key']
        except Exception as e:
            print(e)
            return make_response({"message": "Token not provided"}, 403)
        
        try:
            isBot = chatBots.objects[:1](key=key).first()
            if not isBot:
                return {"message": "chatBot does not exists","status":False}
            else:
                current_time = datetime.datetime.utcnow().date()
                print(current_time)
                if  (isBot.validityEndDate.date() > current_time):
                    bot_data = {}
                    bot_data['name'] = isBot.name
                    bot_data['id'] = str(isBot.id)
                    # bot_data['text'] = [{'_id': str(item['_id']), 'text_data': item['text_data'], 'title': item['title'], 'user_id': item['user_id']} for item in bot.text]
                    bot_data['validityStartDate'] = isBot.validityStartDate
                    bot_data['validityEndDate'] = isBot.validityEndDate
                    bot_data['questions'] = isBot.questions
                    bot_data['plan_id'] = str(isBot.plan_id)
                    if isBot.avatar_image :
                        bot_data['avatar_image']=os.environ.get('url')+isBot.avatar_image  
                    bot_data['created'] = isBot.created.isoformat() 
                    bot_data['user_id'] = str(isBot.user_id)
                    bot_data['key'] = str(isBot.key)
                    bot_data['theme']=isBot.theme
                    bot_data['purpose']=isBot.purpose 
                    bot_data['company_name']=isBot.company_name
                    bot_data['company_description']=isBot.company_description
                    bot_data['support_name']=isBot.support_name
                    bot_data['support_email']=isBot.support_email
                    bot_data['intro_message']=isBot.intro_message
                    bot_data['support_mobile']=isBot.support_mobile
                    bot_data['enableSupport']=isBot.enableSupport
                    bot_data['getCustomerInfo']=isBot.getCustomerInfo
                    bot_data['getMobile']=isBot.getMobile
                    bot_data['getEmail']=isBot.getEmail
                    bot_data['chatbot_color']=isBot.chatbot_color
                    if(isBot.facebookData):
                        bot_data['useFaceBook']=isBot.useFaceBook
                        bot_data['fb_url'] = isBot.facebookData.get('url', None)
                    else:
                        bot_data['useFaceBook']=False
                    if(isBot.whatsappData):
                        bot_data['useWhatsApp']=isBot.useWhatsApp
                        bot_data['wa_url'] = isBot.whatsappData.get('url', None)
                    else:
                        bot_data['useWhatsApp']=False
                    session['myBot'] = bot_data
                    return func(*args, **kwargs)
                else:
                    return {"message": "Validity Expired","status":False}
        except Exception as e: 
            print(e)
            return make_response({"message": "Invalid token provided","status":False})   
    wrapper.__name__ = func.__name__
    return wrapper