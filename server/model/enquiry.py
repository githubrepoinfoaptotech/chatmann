from mongoengine import Document, StringField, EmailField,BooleanField,DateTimeField,FloatField,ObjectIdField,IntField,ListField,DictField
from bson import ObjectId
import datetime

class Enquiry(Document):
    chatbot_id=ObjectIdField(required=True)
    name=StringField(required=True, max_length=40)
    email = EmailField(required=True, max_length=1024)
    mobile = StringField(required=True, max_length=256)
    message= StringField(required=True)
    created = DateTimeField(default=datetime.datetime.utcnow)
    updated = DateTimeField(default=datetime.datetime.utcnow) 