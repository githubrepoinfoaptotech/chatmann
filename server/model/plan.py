from mongoengine import Document, StringField, EmailField,BooleanField,DateTimeField,FloatField,IntField
from bson import ObjectId
import datetime
class Plans(Document):
    price=FloatField(required=True, max_length=24)
    validity=StringField(required=True, max_length=40)
    about=StringField()
    title=StringField(required=True, max_length=24)
    questions=IntField(required=True)
    country_code=StringField()
    currency=StringField()
    tax_perc=FloatField()
    plan_order=IntField()
    plan_code=StringField()
    token_limit=IntField(required=True)
    isActive=BooleanField()
    created = DateTimeField(default=datetime.datetime.utcnow)
    updated = DateTimeField(default=datetime.datetime.utcnow)