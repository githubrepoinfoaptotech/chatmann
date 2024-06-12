from model.chatbot import chatBots
from model.plan import Plans
from model.userChatHistory import userChatHistory
from model.user import Users
import json

from flask import jsonify, make_response,session, render_template, request
import os
from werkzeug.utils import secure_filename
from utils.functions import checkValidity,pdfReader,docuentReader,xlReader,xlsxReader
import datetime
import uuid
import time
import secrets
import string
from datetime import timedelta
from bson import ObjectId
from langchain.text_splitter import RecursiveCharacterTextSplitter

from config import client,llm,openai_ef,embedding_function
from langchain.vectorstores import Chroma
import time
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import AsyncChromiumLoader
from langchain.document_transformers import BeautifulSoupTransformer
from langchain.document_transformers import Html2TextTransformer
from utils.sendMail import send_verification_quota
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
from urllib.parse import urlparse
import requests
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

import urllib.request
import ssl
from bs4 import BeautifulSoup
from urllib.parse import urlparse



def add_chatbot_text_bykey(data):
    try:
        myBot=session['myBot']
        print(myBot['id'])
        isBot= chatBots.objects[:1](id=myBot['id']).first()
        if not isBot:
                return {"message": "chatBot does not exists","status":False}
        else:  
            current_time=datetime.datetime.utcnow()
            if (isBot.used_characters+len(data['text'])<isBot.allowed_characters):
                if (isBot.validityEndDate>current_time):
                    saveData={}
                    saveData['_id'] = ObjectId()
                    saveData['text_data'] = data['text']
                    saveData['length']=len(data['text'])
                    saveData['title'] = data['title']
                    isBot.text.append(saveData)
                    # isBot.used_characters=isBot.used_characters+len(textData['text'])
                    isBot.save()    
                    isBot.update(botTraining="Pending")
                    # text_data_concatenated = textData['text']
                    # saveText(isBot.key,text_data_concatenated)
                    data['id']=myBot['id']
                    return {"message": "ChatBot Text Added Successfully","status":True,'update_id':str(saveData['_id']),'res_data':data}
                else:
                    return {"message": "Validity Expired","status":False}
            else:
                return {'message': "You dont have enough token to train","status":False}
    except Exception as e:
        return make_response({'message': str(e),"status":False}, 404) 