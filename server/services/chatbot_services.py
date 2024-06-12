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
from utils.sendMail import send_verification_quota,send_customer_inquiry
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

import pandas as pd
   

def checkReminder(bot):
    try:
        if int(bot['questions'])==50:
            # Get the current date and time
            now = datetime.datetime.now()
            # Format the date as "Oct-10-YYYY"
            formatted_date = now.strftime("%b-%d-%Y")
            myuser=Users.objects[:1](id=bot['user_id']).first()
            plan=Plans.objects[:1](id=bot['plan_id']).first()
            usedamount=(int(plan.questions)-49)
            totalamount=int(plan.questions)
            remainingamount=int(plan.questions)-usedamount
            email_content = render_template(
                'quota_reminder_template.html',
                name=myuser.name,
                sitename="Infoapto",
                usedamount=usedamount,
                totalamount=totalamount,
                remainingamount=remainingamount,
                date=formatted_date
            )
            html =email_content
            subject = "Quota Remainder!!"
            to_address = myuser.email
            receiver_username = myuser.name
            # Send the email and store the response
            email_response = send_verification_quota(subject, html, to_address, receiver_username)
        elif int(bot['questions'])==20:
            # Get the current date and time
            now = datetime.datetime.now()
            # Format the date as "Oct-10-YYYY"
            formatted_date = now.strftime("%b-%d-%Y")
            myuser=Users.objects[:1](id=bot['user_id']).first()
            plan=Plans.objects[:1](id=bot['plan_id']).first()
            usedamount=(int(plan.questions)-19)
            totalamount=int(plan.questions)
            remainingamount=int(plan.questions)-usedamount
            email_content = render_template(
                'quota_reminder_template.html',
                name=myuser.name,
                sitename="Infoapto",
                usedamount=usedamount,
                totalamount=totalamount,
                remainingamount=remainingamount,
                date=formatted_date
            )
            html = email_content
            subject = "Quota Remainder!!"
            to_address = myuser.email
            receiver_username = myuser.name
            # Send the email and store the response
            email_response = send_verification_quota(subject, html, to_address, receiver_username)
        elif int(bot['questions'])==1:
            # Get the current date and time
            now = datetime.datetime.now()
            # Format the date as "Oct-10-YYYY"
            formatted_date = now.strftime("%b-%d-%Y")
            myuser=Users.objects[:1](id=bot['user_id']).first()
            plan=Plans.objects[:1](id=bot['plan_id']).first()
            usedamount=(int(plan.questions)-1)
            totalamount=int(plan.questions)
            remainingamount=int(plan.questions)-usedamount
            email_content = render_template(
                'quota_reminder_template.html',
                name=myuser.name,
                sitename="Infoapto",
                usedamount=usedamount,
                totalamount=totalamount,
                remainingamount=remainingamount,
                date=formatted_date
            )
            html = email_content
            subject = "Quota Remainder!!"
            to_address = myuser.email
            receiver_username = myuser.name
            # Send the email and store the response
            email_response = send_verification_quota(subject, html, to_address, receiver_username)
        else:
            return False    
    except Exception as e: 
        return make_response({'message': str(e),"status":False})   
def update_user_info(data):
    try:
        theBot=session['myBot']
        isUser = userChatHistory.objects[:1](id=data['session_id']).first()
        title=""
        if 'customerMobile'  in data:
            title=data['customerMobile']
        elif 'customerEmail' in data:
            title=data['customerEmail']  
        if title:
            isUser.title=title
            isUser.user_filled=True
            isUser.save()
            my_user=Users.objects[:1](id=isUser['user_id']).first()
            subject = "Customer Inquiry"
            to_address = my_user.email
            receiver_username = my_user.name
            isUser.title=title
            isUser.save()
            now = datetime.datetime.now()
            # Format the date as "Oct-10-YYYY"
            formatted_date = now.strftime("%b-%d-%Y")
            link=os.environ.get("fronEndUrlCustomer")+"?token="+str(isUser.id)+"&api_key="+theBot['key']
            print(link)
            email_content = render_template(
                    'customer_Inquiry_template.html',
                    title=isUser.title,
                    client_name=my_user.name,
                    link=link,
                    date=formatted_date
                )
            html = email_content
            # Send the email and store the response
            email_response = send_customer_inquiry(subject, html, to_address, receiver_username)
            return {'message': "Saved Successfully","status":True}
        else:
            return {'message': "Invalid data","status":False}
    except Exception as e: 
        print(e)
        return make_response({'message': str(e),"status":False}) 
def get_Answer(data):
    try:
        question= data['question']
        theBot=session['myBot']
        isVaild=checkValidity(theBot['id'])
        
        if isVaild:
            if not data['session_id']:
                isUser=userChatHistory(title=question,history=[],user_id=theBot['user_id'],chatbot_id=theBot['id'], category = 'website')
                isUser.save()
            else:
                isUser = userChatHistory.objects[:1](id=data['session_id']).first()
                
            if int(theBot['questions'])>0:
                checkReminder(theBot)
                #embedding_function = OpenAIEmbeddings()
                #embedding_function = OpenAIEmbeddings()
            
                db4 = Chroma(client=client, collection_name=theBot['key'], embedding_function=embedding_function)
                follow_guidelines = True
                
                prompt = ChatPromptTemplate(
                messages=[
                    SystemMessagePromptTemplate.from_template(
                        "You are a nice chatbot having a conversation with a human. Follow these guidelines closely:"
                        "Keep your response within a maximum of 100 words."
                        "Don't act like a third party conveying the message; be the company's own chatbot AI."
                        "You are a chatbot for"+theBot['name']+".Please stick to information provided about the company and avoid asnwering out of context qestions"
                        "Respond to the user like a human if they talk generally and do not make up context out of the provided one."
                        "If you don't have the answer, politely state that you don't know, avoiding fabricated responses."
                        "Employ bullet points solely when essential, such as for creating lists."
                        "Provide as much detail as possible in your response, even when context is limited."
                        "Avoid asking any follow-up questions to the customer."
                        "If user asks out of  the context relevancy please steer back to the to the company you provide information for"
                        "If they say thank you and feel like they are ending the convesation please reply in a humble way you are here for them 24/7 if they need anything else"
                        "Context: {context}"
                    ),
                    HumanMessagePromptTemplate.from_template("{question}")
                ]
            )
                # if follow_guidelines:
                # # Add the guidelines template to the prompt
                #     prompt.messages.insert(0, SystemMessagePromptTemplate.from_template("Follow the guidelines closely and very important thing is humbly decline answering general questions asked!"))
                retriever = db4.as_retriever()
                print(retriever)
                memory=ConversationBufferMemory(memory_key='chat_history', return_messages=True)
        
                qa_chain = ConversationalRetrievalChain.from_llm(
                    llm,
                    retriever=retriever,
                    # chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
                    verbose=True,
                    combine_docs_chain_kwargs={"prompt": prompt}
                    #memory=memory
                )
                if len(isUser.history)>0:
                #conversation({"question": "hi"})
                    my_history=[ ( item['question'], item['answer']) for item in isUser.history[-3:]]
                    # my_history.insert(0, default_history)
                    print(my_history)
                    chain_input = {"question": question, "chat_history": my_history}
                    result = qa_chain(chain_input)
                else:
                    my_history=[] 
                    print(my_history)
                    result = qa_chain({"question": question,"chat_history": my_history})
                saveData={}
                saveData['_id'] = ObjectId()
                saveData['question'] = data['question']
                saveData['answer'] = result['answer'] 
                saveData['created']=datetime.datetime.utcnow() 
                isUser.history.append(saveData)
                isUser.save()
                updateBot(theBot)
                # session_data={}
                # paragraphs = re.split(r'\.\s+', result['answer'])

                return make_response({'message':result['answer'] ,"status":True,"session_id":str(isUser.id),"formFilled":isUser.user_filled}) 
            else:
                return {'message': "Apologies, but I've reached my question limit for this session,please contact the administration!","status":True}
        else:
           response="Thank you for visiting! Our chatbot is currently under development and will be ready soon. We appreciate your patience and can't wait to assist you when it's up and running. If you need immediate help, please contact our support team. Thank you!"
           return make_response({"message":response,"status":True})
    except Exception as e: 
        print(e)
        return make_response({'message': str(e),"status":False}) 
def saveText(key,text):
    #client = chromadb.HttpClient(host="localhost", port=8000)
    collection = client.get_or_create_collection(name=key, embedding_function=openai_ef)
    content =  text
    text_splitter = RecursiveCharacterTextSplitter(
         chunk_size=500, chunk_overlap=50)
    docs = text_splitter.create_documents([content])
    collection_ids=[]  
    for doc in docs:
        uuid_val = uuid.uuid1()
        collection.add(ids=[str(uuid_val)], documents=doc.page_content)
        collection_ids.append(str(uuid_val))
        time.sleep(1)  
    return collection_ids  

def delete_embedding(key):
    try:
        if (client.get_collection(name=key)):
            client.delete_collection(name=key)
    except Exception as e:
       print(e)

def valiadteSameUrl(Url,BaseUrl,cleanUrl)->bool:
    if cleanUrl=="www."+BaseUrl:
        return True
    else:
        switchUrl={
            f"http://{BaseUrl}/":True,
            f"https://{BaseUrl}/":True,
            f"http://{BaseUrl}":True,
            f"https://{BaseUrl}":True
        }
        return switchUrl.get(Url,False);
def get_my_webLinks(data):
    print(data)
    isBot = chatBots.objects[:1](id=data['id']).first()
    # url = data['link']
    # print(url)
    # Send an HTTP GET request to the URL
    # Create a request object and set a User-Agent header to mimic a web browser
    links_with_lengths=[]
    try:
        totalChars=0
        isBot.update(botTraining="Pending")
        myUrls=testing_url(data['link'])
        if len(myUrls)>0:
            
            for url in myUrls:
                loader = AsyncChromiumLoader([url])
                html = loader.load()
                html2text = Html2TextTransformer()
                docs = html2text.transform_documents(html)
                # print(docs[0].page_content)
                # print(len(docs[0].page_content))
                if len(docs[0].page_content) != 0:
                    vector_ids=saveText(isBot.key,docs[0].page_content)
                    totalChars+=len(docs[0].page_content)
                    if(isBot.used_characters+totalChars>=isBot.allowed_characters):
                        totalChars-=len(docs[0].page_content)
                        break
                    else:
                        links_with_lengths.append({"_id":ObjectId(),"url": url, "user_id":isBot.user_id,"length": len(docs[0].page_content),"vector_ids":vector_ids})
            print("done")
            print(links_with_lengths)
            print(totalChars)
            isBot.websiteData.extend(links_with_lengths)
            newCount=isBot.used_characters+totalChars
            isBot.save()
            isBot.update(botTraining="Completed",used_characters=newCount)
            # return make_response({"data": 'data', "status": True}, 200)
        else:
            isBot.update(botTraining="Completed")
    except Exception as e:
        isBot.update(botTraining="Completed")
        print(e)
        # return make_response({'message': str(e), "status": False})
def ClearBaseUrl(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    cleanUrl=domain
    # .replace("www.", "")
    return cleanUrl


def checkUrl(href,base_url):

        notALink=["#","javascript:void(0)","\\'javascript:void(0);\\'","javascript:void(0);","None",None,base_url]
        if(href not in notALink):
            if (href.startswith("/") or href.startswith("./")):
                if(href.startswith("./")):
                    newurl=base_url+href[2:]
                else:
                    newurl=base_url+href[1:]
                return newurl
            else:
                if(href.startswith("#")):
                    return False
                else:
                    if(not href.startswith("http")):
                        return base_url+href
                    else:
                        return href
        else:
            return False
    


def testing_url(url):
    try:
        context = ssl._create_unverified_context()
        base_url=url
        weburl = urllib.request.urlopen(base_url, context=context)
        html_page=str(weburl.read())
        soup=BeautifulSoup(html_page,'lxml')
        links=soup.findAll("a")
        print(links)
        myset=set()
        for link in links:

            href=str(link.get("href")).lower()
            ThisUrl=checkUrl(href,base_url)
            if ThisUrl:
                cleanUrl=ClearBaseUrl(ThisUrl)
                BaseUrl=ClearBaseUrl(base_url)
                print(BaseUrl)
                # myset.add(BaseUrl)
                if (cleanUrl in base_url) or (BaseUrl in cleanUrl):
                    if valiadteSameUrl(ThisUrl,BaseUrl,cleanUrl):
                        print("Not in Url1: ",ThisUrl)
                    elif "?" in ThisUrl:
                        myset.add(ThisUrl.split("?")[0])
                    else:
                        myset.add(ThisUrl)

        print(myset)
        print(len(myset))
        myList=list(myset)
        myList.insert(0, BaseUrl)
        return myList
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        # Handle the error here, for example, return an empty set or log the error.
        return set()
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        # Handle the error here, for example, return an empty set or log the error.
        return set()

def train_bot_text(data,update_id):
    try:
        print("here")
       
        isBot = chatBots.objects[:1](id=data['id']).first()
        # delete_embedding(isBot.key)
        # return False
        bot_text = [{'_id': str(item['_id']),
             'text_data': item['text_data'], 
             'title': item['title'],
             'length':item['length'],
             'vector_ids': item.get('vector_ids', [])  # Use item.get() to provide a default value
            } for item in isBot.text]
        vector_id=saveText(isBot.key,data['text'])
        new_bot_text=[{'_id': item['_id'], 'text_data': item['text_data'],'length':item['length'], 'title': item['title'], 'vector_ids': vector_id} if item['_id'] == update_id else item for item in bot_text]
        isBot.used_characters+=len(data['text'])
        isBot.text=new_bot_text
        isBot.botTraining="Completed"
        isBot.save()
    except Exception as e:
        print(e)
def get_trained_webiste_links(data):
    try:
        
        if 'page' in data:
            page = int(data['page'])
        else:
            page=1
        page_size = int(10)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        isBot = chatBots.objects[:1](id=data['id'],user_id=session['user_id']).only('websiteData').first()
        if not isBot:
            return {"message": "User does not exists","status":False}
        total_len=len(isBot.websiteData)
        paginated_list = isBot.websiteData[start_index:end_index]
        bot_data={}
        bot_data = [{'_id': str(item['_id']), 'url': item['url'],'length':item['length'], 'user_id': str(item['user_id'])} for item in paginated_list ]
        return make_response({"data":bot_data,"status":True,'count':total_len}, 200)
    except Exception as e:
        return make_response({'message': str(e),"status":False})
def delete_website_links(data):
    try:
        newdata=[]
        isBot = chatBots.objects[:1](id=data['id'],user_id=session['user_id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else: 
            bot_website =[{'_id': str(item['_id']), 'url': item['url'], 'user_id': item['user_id'],'length':item['length'],'vector_ids': item.get('vector_ids', [])} for item in isBot.websiteData]
            newdata[:] = [item for item in bot_website if item["_id"] != data['web_id']]
            deletedData = [item for item in bot_website if item["_id"] == data['web_id']]
            # isBot.update(botTraining="Pending")
            isBot.websiteData=newdata
            delete_embedding_data(deletedData[0],isBot.key)
            if(isBot.used_characters-deletedData[0]['length']>0):
                isBot.used_characters-=deletedData[0]['length']
            else:
                isBot.used_characters=0    
            isBot.save() 
            # mylinks = [item["url"] for item in newdata]
            # text=getTexts(mylinks)
            return make_response({"message":"Url Removed successfully","status":True,"RetrainBot":False}, 200)
    except Exception as e:
        return make_response({'message': str(e),"status":False})     
def add_chatbot_support(data):
    try:
       is_bot=chatBots.objects[:1](id=data['id'],user_id=session['user_id']).first()
       if not is_bot:
            return {"message": "ChatBot Not Found","status":False} 
       else:
           is_bot.support_name=data['support_name']
           is_bot.support_email=data['support_email']
           is_bot.support_mobile=data['support_mobile']
           is_bot.save()
           return {"message": "Support Information Updated!","status":True}
    except Exception as e:
       
        return make_response({'message': str(e),"status":False})    
def toggle_customer_info(data):
    try:
       is_bot=chatBots.objects[:1](id=data['id'],user_id=session['user_id']).first()
       if not is_bot:
            return {"message": "ChatBot Not Found","status":False} 
       else:
        is_bot.getCustomerInfo= not is_bot.getCustomerInfo
        is_bot.save()
        if(is_bot.getCustomerInfo==True):
            return {"message": "Get support informnation is active","status":True}
        else:
            return {"message": "Get support informnation is inactive","status":True}      
            
    except Exception as e:
       
        return make_response({'message': str(e),"status":False})        
def toggle_mail_or_email(data):
    try:
       is_bot=chatBots.objects[:1](id=data['id'],user_id=session['user_id']).first()
       if not is_bot:
            return {"message": "ChatBot Not Found","status":False} 
       else:
        if 'getMobile' in data:
               is_bot.getMobile=not is_bot.getMobile
               if is_bot.getMobile==True:
                   is_bot.getEmail=False
        elif 'getEmail' in data:
                is_bot.getEmail=not is_bot.getEmail
                if is_bot.getEmail==True:
                   is_bot.getMobile=False
        is_bot.save()
        return {"message": "Success","status":True} 
    except Exception as e:
       
        return make_response({'message': str(e),"status":False})  
def add_ChatBot(botdata):
    try:
        if session['country_code'] == None:
            return {"message": "Unavailable for your country please contact support for further details!","status":False}
        free_plan=Plans.objects[:1](country_code=session['country_code'],plan_order=1).first()
        if not free_plan:
            return {"message": "Unavailable for your country please contact support for further details!","status":False}
        is_bot=chatBots.objects[:1](name=botdata['name'],user_id=session['user_id'])
        is_free_bot=chatBots.objects[:1](plan_id=free_plan['id'],user_id=session['user_id'])
        if is_bot:
            return {"message": "chatBot Already Exist","status":False} 
        elif is_free_bot:
            return {"message": "Cant create Chatbot ,please upgrade the free chatbot to paid to add a new one!","status":False}
        else:
            current_date = datetime.datetime.utcnow() 
            characters = string.ascii_letters + string.digits
            
            new_date = current_date + timedelta(days=int(os.environ.get('freeDays')))
            chatbot=chatBots(user_id=session['user_id'],name=botdata['name'],theme="primary",validityStartDate = current_date,
            validityEndDate = new_date,questions=int(free_plan['questions']),allowed_characters=int(free_plan['token_limit']),used_characters=0,plan_code=free_plan['plan_code'],plan_id=free_plan['id'])
            chatbot.save()
            random_key = ''.join(secrets.choice(characters) for _ in range(16))
            final_key = str(chatbot.id) + random_key
            chatbot.update(key=final_key)
            return {"message": "Success","data":str(chatbot.id),"status":True}
    except Exception as e:
        
        return make_response({'message': str(e),"status":False})      
def get_ChatBot(botdata):
    try:
        myResponse=[]
        isBot = chatBots.objects[:1](id=botdata['id'],user_id=session['user_id']).first()
        if not isBot:
            return {"message": "User does not exists","status":False}
        # client.delete_collection(name=isBot.key)
        # return make_response({"message":"deleted","status":True}, 200)  
        else: 
            bot_data = {}
            bot_data['_id'] = str(isBot.id)
            bot_data['user_id'] = str(isBot.user_id)
            bot_data['name'] = isBot.name
            # bot_data['text'] = [{'_id': str(item['_id']), 'text_data': item['text_data'], 'title': item['title'], 'user_id': item['user_id']} for item in bot.text]
            bot_data['validityStartDate'] = isBot.validityStartDate
            bot_data['validityEndDate'] = isBot.validityEndDate
            bot_data['questions'] = isBot.questions
            bot_data['used_characters']=isBot.used_characters
            bot_data['allowed_characters']=isBot.allowed_characters
            bot_data['purpose']=isBot.purpose 
            bot_data['company_name']=isBot.company_name
            bot_data['company_description']=isBot.company_description
            bot_data['support_name']=isBot.support_name
            bot_data['support_email']=isBot.support_email
            bot_data['support_mobile']=isBot.support_mobile
            bot_data['intro_message']=isBot.intro_message
            bot_data['theme']=isBot.theme
            bot_data['key']=isBot.key 
            bot_data['botTraining']=isBot.botTraining
            bot_data['enableSupport']=isBot.enableSupport
            bot_data['getCustomerInfo']=isBot.getCustomerInfo
            bot_data['getMobile']=isBot.getMobile
            bot_data['getEmail']=isBot.getEmail
            if isBot.useFaceBook:
                bot_data['useFaceBook']=isBot.useFaceBook
            if isBot.useWhatsApp:
                bot_data['useWhatsApp']=isBot.useWhatsApp
            if isBot.avatar_image:
                bot_data['avatar_image']=os.environ.get('url')+isBot.avatar_image 
            bot_data['created'] = isBot.created.isoformat()
            bot_data['chatbot_color']=isBot.chatbot_color
            return make_response({"data":bot_data,"status":True}, 200)   
    except Exception as e:
        return make_response({'message': str(e)}, 404)
def get_all_ChatBot():
    try:
        myResponse=[]
        isBot = chatBots.objects(user_id=session['user_id'])
        if not isBot:
            return {"message": "User does not exists","status":False}
        else: 
            for bot in isBot:
                plan_data=Plans.objects(id=bot.plan_id).first()
                bot_data = {}
                bot_data['_id'] = str(bot.id)
                bot_data['user_id'] = str(bot.user_id)
                bot_data['name'] = bot.name
                # bot_data['text'] = [{'_id': str(item['_id']), 'text_data': item['text_data'], 'title': item['title'], 'user_id': item['user_id']} for item in bot.text]
                bot_data['validityStartDate'] = bot.validityStartDate
                bot_data['validityEndDate'] = bot.validityEndDate
                bot_data['questions'] = bot.questions
                bot_data['used_characters']=bot.used_characters
                bot_data['allowed_characters']=bot.allowed_characters 
                bot_data['plan_code']=bot.plan_code 
                bot_data['created'] = bot.created.isoformat()
                bot_data['plan_name']=plan_data['title']
                myResponse.append(bot_data)
            return make_response({"data":myResponse,"status":True}, 200)    
    except Exception as e:
        
        return make_response({'message': str(e)}, 404)
def edit_ChatBot(editdata):
    try:
        myResponse=[]
        isBot = chatBots.objects[:1](id=editdata['id'],user_id=session['user_id']).first()
        if not isBot:
            return {"message": "Bot does not exists","status":False}
        else: 
            if 'name' in editdata:
                name=editdata['name']
            else:
                name=isBot.name
            if 'purpose' in editdata:
                purpose=editdata['purpose']
            else:
                name=isBot.purpose
            if 'intro_message' in editdata:
                intro_message=editdata['intro_message']
            else:
                if isBot.intro_message:
                    intro_message=isBot.intro_message
                else:
                    intro_message=""
            isBot.update(name=name,purpose=purpose,intro_message=intro_message)
            return make_response({'message': 'Succesfully Edited',"status":True}, 200) 
    except Exception as e:
        return make_response({'message': str(e),"status":False}, 404)
def get_ChatBot_text(textData):
    try:
        if 'page' in textData:
            page = int(textData['page'])
        else:
            page=1
        page_size = int(10)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        isBot = chatBots.objects[:1](id=textData['id'],user_id=session['user_id']).only('text').first()
        
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else: 
            total_len=len(isBot.text)
            paginated_list = isBot.text[start_index:end_index]
            botData = [{'_id': str(item['_id']), 'text_data': item['text_data'], 'title': item['title'], 'length':item['length']} for item in paginated_list]
            return make_response({'data':botData ,"status":True,"count":total_len}, 200) 
    except Exception as e:
       
        return make_response({'message': str(e)}, 404)    
def get_chatbot_faqs(data):
    try:
        if 'page' in data:
            page = int(data['page'])
        else:
            page=1
        page_size = int(10)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        isBot = chatBots.objects[:1](id=data['id'],user_id=session['user_id']).only('faqData').first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else:
            total_len=len(isBot.faqData)
            paginated_list = isBot.faqData[start_index:end_index]
            bot_faq = [{'_id': str(item['_id']),
                'text': item['text'], 
                'question': item['question'],
                'answer': item['answer'],
                'length':item['length'],
                'vector_ids': item.get('vector_ids', [])  # Use item.get() to provide a default value
                } for item in paginated_list]
            return make_response({'data':bot_faq ,"status":True,"count":total_len}, 200) 
    except Exception as e:
        return make_response({'message': str(e)}, 404) 
def get_chatbot_doc(data):
    try:
        if 'page' in data:
            page = int(data['page'])
        else:
            page=1
        page_size = int(10)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        isBot = chatBots.objects[:1](id=data['id'],user_id=session['user_id']).only('docData').first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else:
            total_len=len(isBot.docData)
            paginated_list = isBot.docData[start_index:end_index]
            bot_doc = [{'_id': str(item['_id']),
             'length': item['length'], 
             'filename': item['filename'],
             'length':item['length'],
             'vector_ids': item.get('vector_ids', [])  # Use item.get() to provide a default value
            } for item in paginated_list]
            return make_response({'data':bot_doc ,"status":True,"count":total_len}, 200) 
    except Exception as e:
        return make_response({'message': str(e)}, 404) 
def add_ChatBot_text(textData):
    try:
        myResponse=[]
        saveData={}
        isBot = chatBots.objects[:1](id=textData['id'],user_id=session['user_id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else: 
            current_time=datetime.datetime.utcnow()
            if (isBot.used_characters+len(textData['text'])<isBot.allowed_characters):
                if (isBot.validityEndDate>current_time):
                    saveData={}
                    saveData['_id'] = ObjectId()
                    saveData['text_data'] = textData['text']
                    saveData['length']=len(textData['text'])
                    saveData['title'] = textData['title']
                    isBot.text.append(saveData)
                    # isBot.used_characters=isBot.used_characters+len(textData['text'])
                    isBot.save()    
                    isBot.update(botTraining="Pending")
                    # text_data_concatenated = textData['text']
                    # saveText(isBot.key,text_data_concatenated)
                    return {"message": "ChatBot Text Added Successfully","status":True,'update_id':str(saveData['_id'])}
                else:
                    return {"message": "Validity Expired","status":False}
            else:
                return {'message': "You dont have enough token to train","status":False}
    except Exception as e:
      
        return make_response({'message': str(e),"status":False}, 404)   
def train_bot_FAQ_byxl(data,id):
    isBot = chatBots.objects[:1](id=id).first()
    totalLen=0
    for mydatas in data:
        mydatas['_id']=ObjectId()
        vector_id=saveText(isBot.key,mydatas['text'])
        mydatas['vector_ids']=vector_id
        totalLen=totalLen+mydatas['length']
        isBot.faqData.append(mydatas)
    isBot.used_characters=totalLen+isBot.used_characters
    isBot.botTraining="Completed"
    isBot.save()
def add_chatbot_FAQ_byxl(data):
        myResponse=[]
        saveData={}
        isBot = chatBots.objects[:1](id=data['id'],user_id=session['user_id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else: 
            # Assuming the Excel file is in XLSX format
            
            # Convert the DataFrame to a list of dictionaries
            training_data=[]
            for datas in data['data']:
                training_object={}
                training_object['text'] = f"Question: {datas['question']}\nAnswer: {datas['answer']}"
                training_object ['question']=datas['question']
                training_object['answer']=datas['answer']
                training_object['length']=len(training_object['text'])
                training_data.append(training_object)
            total_length = 0
            total_length = sum(item.get("length", 0) for item in training_data)
            if(isBot.used_characters+total_length>isBot.allowed_characters):
                return {"message": "You dont have enough token to train!","status":False}
            else:   
                isBot.update(botTraining="Pending")
                return {"message": "ChatBot Text Added Successfully","status":True,'training_data':training_data,'bot_id':data['id']}
def add_chatbot_doc(data):
    try:
        if 'file' not in data.files:
            return jsonify({'message': 'No file part',"status":False})
        isBot = chatBots.objects[:1](id=data.form.get('id'),user_id=session['user_id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        file = data.files['file']

        if file.filename == '':
            return jsonify({'message': 'No selected file',"status":False})
        #current_time = str(datetime.datetime.now().timestamp())
        filename = file.filename
        if(file.filename.endswith('.pdf')):
            text=pdfReader(file)
        elif(file.filename.endswith('.doc') or file.filename.endswith('.docx')):
            print(filename)
            filename = secure_filename(f"{file.filename}")
            path = os.path.join("assets/temp/", filename)
            print(path)
            file.save(path)
            text=docuentReader(path)
            if len(text)>0:
                if os.path.exists(path):
                    os.remove(path)
        elif(file.filename.endswith('.xls') ):
            text=xlReader(file)
        elif(file.filename.endswith('.xlsx')):
            text=xlsxReader(file)
        else:
            return {'message': 'Invalid file format',"status":False}
        docData={}
        docData['_id']=ObjectId()
        docData['length']=len(text)
        docData['filename']=filename
        docData['vector_ids']=[]
        if(isBot.used_characters+docData['length']>isBot.allowed_characters):
                return {"message": "You dont have enough token to train!","status":False}
        isBot.docData.append(docData)
        isBot.save()    
        isBot.update(botTraining="Pending")
        return {"message": "ChatBot Text Added Successfully","status":True,'update_id':str(docData['_id']),'text':text,'bot_id':data.form.get('id')}
    except Exception as e:
        print(e)
        return make_response({'message': str(e)}, 404) 
def add_chatbot_avatar(textData):
    try:
        if 'file' not in textData.files:
            return jsonify({'message': 'No file part',"status":False})
        isBot = chatBots.objects[:1](id=textData.form.get('id'),user_id=session['user_id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        file = textData.files['file']

        if file.filename == '':
            return jsonify({'message': 'No selected file',"status":False})
        current_time = str(datetime.datetime.now().timestamp())
       
        filename = secure_filename(f"{session['user_id']}_{current_time}_{file.filename}")
        if file:
            filename = os.path.join("assets/images/", filename)
            isBot.avatar_image=filename
            file.save(filename)
            isBot.save()
            return jsonify({'message': 'File uploaded successfully',"status":True})
    except Exception as e:
       
        return make_response({'message': str(e)}, 404)   
def delete_ChatBot_text(textData): 
    try:
        newdata=[]
        isBot = chatBots.objects[:1](id=textData['id'],user_id=session['user_id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else: 
            bot_text = [{'_id': str(item['_id']), 'text_data': item['text_data'], 'title': item['title'], 'length':item['length'],'vector_ids':item['vector_ids']} for item in isBot.text]
            newdata[:] = [item for item in bot_text if item["_id"] != textData['text_id']]
            thedata=[item for item in bot_text if item["_id"] == textData['text_id']]
            print(thedata)
            delete_embedding_data(thedata[0],isBot.key)
            isBot.text=newdata
            # newCount = sum(len(item['text_data']) for item in newdata)
            # isBot.used_characters=newCount
            if(isBot.used_characters-len(thedata[0]['text_data'])>0):
                isBot.used_characters-=len(thedata[0]['text_data'])
            else:
                isBot.used_characters=0
            isBot.save()
            return {"message": "ChatBot Text Removed Successfully","status":True}
    except Exception as e:
       
        return make_response({'message': str(e)}, 404)     
def delete_embedding_data(data,key):
    print("in")
    print(data)
    print(data['vector_ids'])
    collection = client.get_or_create_collection(name=key)
    for datas in data['vector_ids']:
        collection.delete(datas)
def delete_all_chatbot_embeddings(key,data):
    print("in")
    print(data)
    collection = client.get_or_create_collection(name=key)
    for datas in data:
        collection.delete(datas)
def add_chatbot_FAQ(data):
        myResponse=[]
        saveData={}
        isBot = chatBots.objects[:1](id=data['id'],user_id=session['user_id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else: 
            current_time=datetime.datetime.utcnow()
            text = f"Question: {data['question']}\nAnswer: {data['answer']}"
            question=data['question']
            answer=data['answer']
            length=len(text)
            if(isBot.used_characters+length>isBot.allowed_characters):
                return {"message": "You dont have enough token to train!","status":False}
            else:
                id=ObjectId()
                isBot.faqData.append({"_id":id,"text":text,"question":question,"answer":answer,"length":length,'vector_ids':[]})
                isBot.save()    
                isBot.update(botTraining="Pending")
                return {"message": "ChatBot Text Added Successfully","status":True,'update_id':str(id),'text':text}

def delete_bot_faq(data):
    try:
        newdata=[]
        isBot = chatBots.objects[:1](id=data['id'],user_id=session['user_id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else: 
            bot_faq = [{'_id': str(item['_id']),
             'text': item['text'], 
             'question': item['question'],
             'answer': item['answer'],
             'length':item['length'],
             'vector_ids': item.get('vector_ids', [])  # Use item.get() to provide a default value
            } for item in isBot.faqData]
            newdata[:] = [item for item in bot_faq if item["_id"] != data['faq_id']]
            thedata=[item for item in bot_faq if item["_id"] == data['faq_id']]
            print(thedata)
            delete_embedding_data(thedata[0],isBot.key)
            isBot.faqData=newdata
            # newCount = sum(len(item['text_data']) for item in newdata)
            # isBot.used_characters=newCount
            if(isBot.used_characters-len(thedata[0]['text'])>0):
                isBot.used_characters-=len(thedata[0]['text'])
            else:
                isBot.used_characters=0
            isBot.save()
            return {"message": "ChatBot faq Removed Successfully","status":True}
    except Exception as e:
       
        return make_response({'message': str(e)}, 404)   
def delete_bot_doc(data):
    try:
        newdata=[]
        isBot = chatBots.objects[:1](id=data['id'],user_id=session['user_id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else: 
            bot_doc = [{'_id': str(item['_id']),
             'length': item['length'], 
             'filename': item['filename'],
             'length':item['length'],
             'vector_ids': item.get('vector_ids', [])  # Use item.get() to provide a default value
            } for item in isBot.docData]
            newdata[:] = [item for item in bot_doc if item["_id"] != data['doc_id']]
            thedata=[item for item in bot_doc if item["_id"] == data['doc_id']]
            delete_embedding_data(thedata[0],isBot.key)
            isBot.docData=newdata
            # newCount = sum(len(item['text_data']) for item in newdata)
            # isBot.used_characters=newCount
            if(isBot.used_characters-thedata[0]['length']>0):
                isBot.used_characters-=thedata[0]['length']
            else:
                isBot.used_characters=0
            isBot.save()
            return {"message": "ChatBot faq Removed Successfully","status":True}
    except Exception as e:
       
        return make_response({'message': str(e)}, 404)  
def train_bot_faq(data,id,text):
    try:
        print("here")
        isBot = chatBots.objects[:1](id=data['id']).first()
        # delete_embedding(isBot.key)
        # return False

        bot_faq = [{'_id': str(item['_id']),
             'text': item['text'], 
             'question': item['question'],
             'answer': item['answer'],
             'length':item['length'],
             'vector_ids': item.get('vector_ids', [])  # Use item.get() to provide a default value
            } for item in isBot.faqData]
        print(bot_faq)
        vector_id=saveText(isBot.key,text)
        print(vector_id)
        new_bot_text=[{'_id': str(item['_id']),
             'text': item['text'], 
             'question': item['question'],
             'answer': item['answer'],
             'length':item['length'], 'vector_ids': vector_id} if item['_id'] == id else item for item in bot_faq]
        isBot.used_characters+=len(text)
        isBot.faqData=new_bot_text
        isBot.botTraining="Completed"
        isBot.save()
    except Exception as e:
            print(e)
def train_bot_doc(data,id,text):
    try:
        print("here")
        isBot = chatBots.objects[:1](id=data).first()
        # delete_embedding(isBot.key)
        # return False

        bot_doc = [{'_id': str(item['_id']),
             'length': item['length'], 
             'filename': item['filename'],
             'length':item['length'],
             'vector_ids': item.get('vector_ids', [])  # Use item.get() to provide a default value
            } for item in isBot.docData]
        print(bot_doc)
        vector_id=saveText(isBot.key,text)
        print(vector_id)
        new_bot_text=[{'_id': str(item['_id']),
             'length': item['length'], 
             'filename': item['filename'],'vector_ids': vector_id} if item['_id'] == id else item for item in bot_doc]
        isBot.used_characters+=len(text)
        isBot.docData=new_bot_text
        isBot.botTraining="Completed"
        isBot.save()
    except Exception as e:
            print(e)

def get_history(data):
    try:
      if data['page']:
            page=data['page']
      else:
            page=0  
      per_page=10
      skip = (page - 1) * per_page
      isUser = userChatHistory.objects[:1](id=data['id'],user_id=session['user_id'],chatbot_id=data['chatbot_id']).first()
      if not isUser:
         return {"message": "NewUser","data":[],"status":True}    
      else:
         botHistory = [{'_id': str(item['_id']), 'question': item['question'], 'answer': item['answer'],'created':item['created']} for item in isUser.history]
         start_index = len(botHistory) - (page * per_page)
         end_index = len(botHistory) - ((page - 1) * per_page)
         # Slice the data to get the current page's data
         myhistory = botHistory[start_index:end_index]
         return make_response({"data": myhistory,"status":True}) 
    except Exception as e:
            
            return make_response({'message': str(e)}, 404) 
def get_history_bykey(data):
    try:
      if data['page']:
            page=data['page']
      else:
            page=0  
      per_page=10
      skip = (page - 1) * per_page
      isUser = userChatHistory.objects[:1](id=data['session_id']).first()
      my_bot= chatBots.objects[:1](id=isUser.chatbot_id).first()
      if not isUser:
         return {"message": "NewUser","data":[],"status":True}    
      else:
         botHistory = [{'_id': str(item['_id']), 'question': item['question'], 'answer': item['answer'],'created':item['created']} for item in isUser.history]
         start_index = len(botHistory) - (page * per_page)
         end_index = len(botHistory) - ((page - 1) * per_page)
         # Slice the data to get the current page's data
         myhistory = botHistory[start_index:end_index]
         return make_response({"data": myhistory,"status":True,"botName":my_bot.name,"customer":isUser.title}) 
    except Exception as e:
            
            return make_response({'message': str(e)}, 404)
def get_chatBot_Bykey():
    try:
       
        theBot=session['myBot']
        # isValid=checkValidity(theBot['id'])
        return make_response({"data": theBot,"status":True})
        # if(isValid):
        #     return make_response({"data": theBot,"status":True}) 
        # else:
        #     response="Thank you for visiting! Our chatbot is currently under development and will be ready soon. We appreciate your patience and can't wait to assist you when it's up and running. If you need immediate help, please contact our support team. Thank you!"
        #     return make_response({"message":response,"status":True,"data": theBot})
    except Exception as e:
           
            return make_response({'message': str(e)}, 404) 
    
def updateBot(data):
    isBot = chatBots.objects[:1](user_id=data['user_id'],key=data['key']).first()
    if not isBot:
        return {"message": "chatBot does not exists","status":False}
    else:
        isBot.questions=isBot.questions-1
        isBot.save()
def update_company_details(data):
    try:
        isBot = chatBots.objects[:1](user_id=session['user_id'],id=data['id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else:
            isBot.company_name=data['company_name']
            isBot.company_description=data['company_description']
            isBot.save()
            return {"message": "Company Data Saved","status":True} 
    except Exception as e:
            
            return make_response({'message': str(e)}, 404)     
def get_chatBot_plan(data):
    try:
        isBot = chatBots.objects[:1](user_id=session['user_id'],id=data['id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else:
            plan=Plans.objects[:1](id=isBot['plan_id']).first()
            if plan:
                plan_data={'_id': str(plan.id), 'price': plan.price, 'validity': plan.validity,  'title': plan.title, 'questions': plan.questions, 'token_limit': plan.token_limit, 'created': plan.created}
                return make_response({"data": plan_data,"status":True})
            else:
                return {"message": "No plan found! Please upgrade.","status":False}
    except Exception as e:
            
            return make_response({'message': str(e)}, 404) 
def get_chat_users(data):
    try:
        if data['page']:
            page=data['page']
        else:
            page=0  
        per_page=10      
        skip = (page - 1) * per_page
        isBot = userChatHistory.objects(user_id=session['user_id'],chatbot_id=data['id'],category=data['category']).skip(skip).limit(per_page)
        count = userChatHistory.objects(user_id=session['user_id'],chatbot_id=data['id'],category=data['category']).count()
        if not isBot:
            return {"message": "Chat does not exists","data":[],"status":False}
        else:
           user_data= [{'id': str(item['id']), 'title': item['title']} for item in isBot]
           return make_response({"data": user_data,"count":count,"status":True})
    except Exception as e:
            
            return make_response({'message': str(e)}, 404)        
def set_chat_bot_theme(data):
    try:
        isBot = chatBots.objects[:1](user_id=session['user_id'],id=data['id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else:
            isBot.theme=data['theme']
            isBot.save()
            return {"message": "Theme Changed","status":True} 
    except Exception as e:
           
            return make_response({'message': str(e)}, 404)   
def setup_facebook_data(data):
    try:
        isBot = chatBots.objects[:1](user_id=session['user_id'],id=data['id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else:
            facebookData={}
            facebookData['fbPageId']=data['fbPageId']
            facebookData['fbPageAccessToken']=data['fbPageAccessToken']
            facebookData['url']=os.environ.get('facebook_url')+facebookData['fbPageId']
            isBot.facebookData=facebookData
            isBot.save()
            return {"message": "Successfully Added","status":True} 
    except Exception as e:
            print(e)
            return make_response({'message': str(e)}, 404)   
def setup_whatsapp_data(data):
    try:
        isBot = chatBots.objects[:1](user_id=session['user_id'],id=data['id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else:
            whatsappData={}
            whatsappData['waBusinessId']=data['waBusinessId']
            whatsappData['accessToken']=data['accessToken']
            whatsappData['phoneNumberId']=data['phoneNumberId']
            responseData=getPhonenumber(data['phoneNumberId'],data['accessToken'])
            if(responseData):
                mobile = re.sub(r'[^a-zA-Z0-9]', '', responseData)
                whatsappData['mobile']=mobile
                whatsappData['url']=os.environ.get('whatsapp_url')+whatsappData['mobile']
                isBot.useWhatsApp=True
            else:
                isBot.whatsappData=whatsappData
                isBot.useWhatsApp=False
                isBot.save()
            return {"message": "Successfully Added","status":True} 
    except Exception as e:
           
            return make_response({'message': str(e)}, 404)  
def setup_webhook_data(data):
    try:
        isBot = chatBots.objects[:1](user_id=session['user_id'],id=data['id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else:
            webHookData={}
            webHookData['webhook_url']=data['webhook_url']
            webHookData['webhook_token']=data['webhook_token']
            isBot.webHookData=webHookData
            isBot.save()
            return {"message": "Successfully Added","status":True} 
    except Exception as e:
           
            return make_response({'message': str(e)}, 404)  
def get_webhook_data(data):
    try:
        isBot = chatBots.objects[:1](user_id=session['user_id'],id=data['id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else:
            if isBot.webHookData:
                webHookData={}
                webHookData['webhook_url']=isBot.webHookData['webhook_url']
                webHookData['webhook_token']=isBot.webHookData['webhook_token']
                return make_response({"data":webHookData,"status":True}, 200)
            else:
                return {"message": "Whatsapp not set up for this chatbot","status":False}
    except Exception as e:
            
            return make_response({'message': str(e)}, 404)
def get_whatsapp_data(data):
    try:
        isBot = chatBots.objects[:1](user_id=session['user_id'],id=data['id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else:
            if isBot.whatsappData:
                whatsappData={}
                whatsappData['waBusinessId']=isBot.whatsappData['waBusinessId']
                whatsappData['accessToken']=isBot.whatsappData['accessToken']
                whatsappData['phoneNumberId']=isBot.whatsappData['phoneNumberId']
                return make_response({"data":whatsappData,"status":True}, 200)
            else:
                return {"message": "Whatsapp not set up for this chatbot","status":False}
    except Exception as e:
            
            return make_response({'message': str(e)}, 404)  
def get_facebook_data(data):
    try:
        isBot = chatBots.objects[:1](user_id=session['user_id'],id=data['id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else:
            if isBot.facebookData:
                facebookData={}
                facebookData['fbPageId']=isBot.facebookData['fbPageId']
                facebookData['fbPageAccessToken']=isBot.facebookData['fbPageAccessToken']
                return make_response({"data":facebookData,"status":True}, 200)
            else:
                return {"message": "Facebook not set up for this chatbot","status":False}
    except Exception as e:
           
            return make_response({'message': str(e)}, 404)   
def toggle_support(data):
    try:
        isBot = chatBots.objects[:1](user_id=session['user_id'],id=data['id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else:
            if((isBot.support_mobile) or (isBot.support_email) or (isBot.support_name)):
                if(isBot.enableSupport):
                    if isBot.enableSupport==True:
                        isBot.enableSupport=False
                        retData={"message": "ChatBot enquiry disabled","status":True}
                    else:
                        isBot.enableSupport=True
                        retData={"message": "ChatBot enquiry enabled","status":True}
                else:    
                    isBot.enableSupport=True
                    retData={"message": "ChatBot enquiry enabled","status":True}
            else:
                isBot.enableSupport=False
                retData={"message": "Fill ChatBot enquiry to enable","status":False}
        isBot.save()
        return retData
    except Exception as e:
            return make_response({'message': str(e),"status":False}, 404)   
def toggel_whatsapp(data):
    try:
        isBot = chatBots.objects[:1](user_id=session['user_id'],id=data['id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else:
            if('whatsappData' in isBot):
                if(isBot.useWhatsApp):
                    if isBot.useWhatsApp==True:
                        isBot.useWhatsApp=False
                        retData={"message": "ChatBot Whatsapp disabled","status":True}
                    else:
                        if 'whatsappData' in isBot :
                            valid=getPhonenumber(isBot['whatsappData']['phoneNumberId'],isBot['whatsappData']['accessToken'])
                            if(valid):
                                isBot.useWhatsApp=True
                                retData={"message": "ChatBot Whatsapp enabled","status":True}
                            else:
                                isBot.useWhatsApp=False
                                retData={"message": "Improper settings to enable  Whatsapp","status":True}
                        else:
                            isBot.useWhatsApp=False
                            retData={"message": "Improper settings to enable  Whatsapp","status":True}
                else:    
                    isBot.useWhatsApp=True
                    retData={"message": "ChatBot Whatsapp enabled","status":True}
            else:
                isBot.useWhatsApp=False
                retData={"message": "Fill whatsapp data to enable","status":False}
        isBot.save()
        return retData
    except Exception as e:
        return make_response({'message': str(e),"status":False}, 404)   
def toggel_facebook(data):
    try:
        isBot = chatBots.objects[:1](user_id=session['user_id'],id=data['id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else:
            if('facebookData' in isBot):
                if(isBot.useFaceBook):
                    if isBot.useFaceBook==True:
                        isBot.useFaceBook=False
                        retData={"message": "ChatBot facebook disabled","status":True}
                    else:
                        isBot.useFaceBook=True
                        retData={"message": "ChatBot facebook enabled","status":True}
                else:    
                    isBot.useFaceBook=True
                    retData={"message": "ChatBot facebook enabled","status":True}
            else:
                isBot.useFaceBook=True
                retData={"message": "Fill facebook data to enable","status":False}
        isBot.save()
        return retData
    except Exception as e:
            return make_response({'message': str(e),"status":False}, 404)   
            
def set_chatbot_color(data):
    try:
        isBot = chatBots.objects[:1](user_id=session['user_id'],id=data['id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else:
            if('chatbot_color' in isBot):
                isBot.chatbot_color['backGroundColor']=str(data['backGroundColor'])
                isBot.chatbot_color['fontColor']=str(data['fontColor'])
                
            else:
                mydata={}
                mydata['backGroundColor']=str(data['backGroundColor'])
                mydata['fontColor']=str(data['fontColor'])
                isBot.update(chatbot_color=mydata)
        isBot.save()
        return {"message": "Chatbot color set successfully","status":True}
    except Exception as e:
            return make_response({'message': str(e),"status":False}, 404)

def delete_chatbot(data):
    try:
        isBot=chatBots.objects[:1](user_id=session['user_id'],id=data['id']).first()
        if not isBot:
            return {"message": "chatBot does not exists","status":False}
        else:
            return {"message": "ChatBot Deleted Successfully.It may take a while for the removal of the chatbot try to check back in few minutes.","status":True,"bot":isBot.id}
    except Exception as e:
            return make_response({'message': str(e),"status":False}, 404)
def delete_embeddings(myid):
    print("in")
    isBot=chatBots.objects[:1](id=myid).first()
    if 'text' in isBot and len(isBot.text)>0:
        for data in isBot.text:
            delete_all_chatbot_embeddings(isBot.key,data['vector_ids'])
    if 'websiteData' in isBot and len(isBot.websiteData)>0:
        for data in isBot.websiteData:
            delete_all_chatbot_embeddings(isBot.key,data['vector_ids'])
    if 'faqData' in isBot and len(isBot.websiteData)>0:
        for data in isBot.faqData:
            delete_all_chatbot_embeddings(isBot.key,data['vector_ids'])
    if 'docData' in isBot and len(isBot.websiteData)>0:
        for data in isBot.docData:
            delete_all_chatbot_embeddings(isBot.key,data['vector_ids']) 
    isBot.delete()    
def getPhonenumber(phoneNumberId,token):
    url="https://graph.facebook.com/v15.0/"+phoneNumberId
    headers = {
    'Content-Type': 'application/json',
    'Authorization':'Bearer '+token
    }
    payload = json.dumps({
    "messaging_product": "whatsapp"})
    response = requests.request("GET", url, headers=headers,data=payload)
    if response.status_code == 200:
        json_data = json.loads(response.text)
        return json_data['display_phone_number']
    else:
        return False
def checkValidToken(token):
    response = requests.get(f"https://graph.facebook.com/v13.0/debug_token", params={
        "input_token": token
    })

    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}).get("is_valid", False)
    else:
        return False
