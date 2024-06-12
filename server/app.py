import os
from flask import Flask,request,jsonify
from flask_cors import CORS
from api.user import user_route 
from api.payment import payment_route
from api.chatbot import chatbot_route
from api.enquiry import enquiry_route
from api.whatsappMessage import whatsapp_route
from api.facebookMessage import facebook_route
from api.external import external_route
from api.superadmin import su_route
from mongoengine import connect 
from api.directory import static_bp
from dotenv import load_dotenv 
import warnings
import ssl





load_dotenv()
secret = os.environ.get('TOKEN_SECRET')
warnings.filterwarnings("ignore")
app = Flask(__name__) 

app.register_blueprint(user_route)
app.register_blueprint(payment_route)
app.register_blueprint(chatbot_route)
app.register_blueprint(enquiry_route)
app.register_blueprint(whatsapp_route)
app.register_blueprint(facebook_route)
app.register_blueprint(external_route)
app.register_blueprint(su_route)
app.register_blueprint(static_bp)
# app.register_blueprint(product_route)
app.secret_key = secret
CORS(app, resources={r"/*": {"origins": "*"}})

connect(host=os.environ.get('Pro_mongo_uri'))


ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('ca.crt', 'ca.key')



if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0",port=8443,ssl_context=ssl_context)






 