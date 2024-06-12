from mongoengine import Document, StringField, EmailField,BooleanField,DateTimeField,FloatField,ListField,DictField,ObjectIdField
from bson import ObjectId
import datetime
class userChatHistory(Document):
    title=StringField(required=True, max_length=250)
    category=StringField()
    history=ListField(DictField(
        _id=ObjectIdField(),
        phonenumberId=StringField(),
        waMessageId=StringField(),
        question=StringField(),
        answer=StringField(),
        created = DateTimeField()
    ))
    user_filled=BooleanField(default=False)
    user_id=ObjectIdField(required=True)
    chatbot_id=ObjectIdField(required=True)
    created = DateTimeField(default=datetime.datetime.utcnow)
    updated = DateTimeField(default=datetime.datetime.utcnow)