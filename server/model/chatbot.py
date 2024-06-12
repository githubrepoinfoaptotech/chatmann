from mongoengine import Document, StringField, EmailField,BooleanField,DateTimeField,FloatField,ObjectIdField,IntField,ListField,DictField
from bson import ObjectId
import datetime
class chatBots(Document):
    user_id=ObjectIdField(required=True)
    allowed_characters=IntField(max_length=10,null=True,default=0)
    used_characters=IntField(max_length=10,null=True,default=0)
    name=StringField(required=True, max_length=40)
    text = ListField(DictField(
        _id=ObjectIdField(),
        text_data=StringField(),
        length=IntField(),
        title=StringField(),
        vector_ids=ListField()
    ))
    websiteData=ListField(DictField(
        _id=ObjectIdField(),
        url=StringField(),
        length=IntField(),
        vector_ids=ListField()
    ))
    validityStartDate=DateTimeField(null=True)
    validityEndDate=DateTimeField(null=True)
    purpose=StringField(max_length=40,null=True)
    questions=IntField(max_length=10,null=True)
    key=StringField(max_length=40)
    avatar_image=StringField()
    company_name=StringField(max_length=40)
    company_description=StringField()
    plan_id=ObjectIdField()
    support_name=StringField(max_length=40)
    support_email=StringField(max_length=40)
    support_mobile=StringField(max_length=40)
    plan_code=StringField(max_length=40)
    theme=StringField(max_length=40)
    intro_message=StringField()
    botTraining=StringField()
    facebookData=DictField(
        # fbAppId=StringField(),
        # fbAppSecret=StringField(),
        # fbPageName=StringField(),
        fbPageId=StringField(),
        fbPageAccessToken=StringField(),
        url=StringField()

    )
    whatsappData=DictField(
        waBusinessId=StringField(),
        accessToken=StringField(),
        phoneNumberId=StringField(),
        mobile=StringField(),
        url=StringField()
    )
    faqData=ListField(DictField(
        _id=ObjectIdField(),
        question=StringField(),
        answer=StringField(),
        text=StringField(),
        length=IntField(),
        vector_ids=ListField()
    ))
    docData=ListField(DictField(
        _id=ObjectIdField(),
        filename=StringField(),
        length=IntField(),
        vector_ids=ListField()
    ))
    webHookData=DictField(
        webhook_url=StringField(),
        webhook_token=StringField()
    )
    useFaceBook=BooleanField(default=False)
    useWhatsApp=BooleanField(default=False)
    enableSupport=BooleanField(default=False)
    getCustomerInfo=BooleanField(default=True)
    getMobile=BooleanField(default=False)
    getEmail=BooleanField(default=True)
    chatbot_color=DictField(
        backGroundColor=StringField(),
        fontColor=StringField()
    )
    created = DateTimeField(default=datetime.datetime.utcnow)
    updated = DateTimeField(default=datetime.datetime.utcnow) 
