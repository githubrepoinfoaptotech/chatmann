from mongoengine import Document, StringField, EmailField,BooleanField,DateTimeField
from bson import ObjectId
import datetime
class Instances(Document):
    user_id = StringField(required=True, max_length=24)
    instance_key=StringField(required=True, max_length=100)
    instance_secret=StringField(required=True, max_length=100)
    validity_start_date=DateTimeField()
    validity_end_date=DateTimeField()
    created = DateTimeField(default=datetime.datetime.utcnow)
    updated = DateTimeField(default=datetime.datetime.utcnow)