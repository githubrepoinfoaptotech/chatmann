from mongoengine import Document, StringField, EmailField,BooleanField,DateTimeField,FloatField,ListField,DictField,ObjectIdField
from bson import ObjectId
import datetime
class userChatHistory(Document):
    phonenumbeId=StringField(required=True, max_length=250)
    phonenumber=StringField()
    category=StringField()
    history=ListField(DictField(
        _id=ObjectIdField(),
        waMessageId=StringField(),
        question=StringField(),
        answer=StringField(),
        created = DateTimeField()
    ))
    user_id=ObjectIdField(required=True)
    chatbot_id=ObjectIdField(required=True)
    created = DateTimeField(default=datetime.datetime.utcnow)
    updated = DateTimeField(default=datetime.datetime.utcnow)