from mongoengine import Document, StringField, EmailField,BooleanField,DateTimeField,FloatField,ObjectIdField
from bson import ObjectId
import datetime
class User_transactions(Document):
    user_id = ObjectIdField(required=True)
    chatbot_id=ObjectIdField(required=True)
    total_amount=FloatField(required=True, max_length=24)
    order_id=StringField(max_length=40)
    currency=StringField(required=True, max_length=40)
    plan_id=StringField(required=True, max_length=24)
    status=StringField(required=True, max_length=24)
    created = DateTimeField(default=datetime.datetime.utcnow)
    updated = DateTimeField(default=datetime.datetime.utcnow)