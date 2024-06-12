from mongoengine import Document, StringField, EmailField,BooleanField,DateTimeField
from bson import ObjectId
import datetime
class Users(Document):
    name = StringField(required=True, max_length=50)
    role = StringField(required=True, max_length=20)
    # address = StringField(required=True, max_length=200)
    referal_code=StringField( max_length=20)
    refered_by=StringField( max_length=20)
    email = EmailField(required=True, max_length=1024)
    mobile = StringField( max_length=256)
    type=StringField()
    google_id=StringField()
    facebook_id=StringField()
    password = StringField(min_length=8,max_length=1024)
    is_Active = BooleanField(required=True)
    is_email_verified = BooleanField(required=True)
    created = DateTimeField(default=datetime.datetime.utcnow)
    updated = DateTimeField(default=datetime.datetime.utcnow) 
    verify_id = StringField(required=True, max_length=24, unique=True, default=lambda: str(ObjectId()))  # Use ObjectId as default
    