from model.chatbot import chatBots
from model.plan import Plans
from model.userChatHistory import userChatHistory
from model.user import Users
from flask import jsonify, make_response,session, render_template, request
from werkzeug.utils import secure_filename
import datetime
from bson import ObjectId
from config import client,llm,openai_ef,embedding_function
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from utils.sendMail import send_verification_quota
from urllib.request import  urlopen
from urllib.parse import urlparse
import requests
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import json
from utils.functions import checkValidity
def recive_whatsapp_message(data): 
    print(data)
    values=data['values']
    type=values[0]['changes'][0]['value']['messages'][0]['type']
    phone_number_id=values[0]['changes'][0]['value']['metadata']['phone_number_id']
    mobile=values[0]['changes'][0]['value']['messages'][0]['from']
    waMessageId=values[0]['changes'][0]['value']['messages'][0]['id']
    print(mobile)
    isBot = chatBots.objects[:1](whatsappData__phoneNumberId=phone_number_id).order_by('-created').first()
    print(isBot.name)
    isValid=checkValidity(isBot['id'])
    if(isValid):
        if(isBot):
                if type=='text':
                    print(type)
                    markMessageRead(isBot,waMessageId,phone_number_id)
                    message=values[0]['changes'][0]['value']['messages'][0]['text']['body']
                    myanswer=getAnswer(isBot,message,mobile,waMessageId,phone_number_id)
                    if myanswer['status']==True:
                        mymessage=myanswer['message']
                        sendReply(mymessage,phone_number_id,mobile,isBot)
                        return {"message":"Returned","status":True}
                    return {"message":"mesage","status":True}
                else:
                    mymessage="Apologies, but "+isBot.name+" can only accept plain text messages. Please ensure your message is in text format without any special characters or images."
                    sendReply(mymessage,phone_number_id,mobile,isBot)
                    return {"message":"Not a text message","status":True}
    else:
        markMessageRead(isBot,waMessageId,phone_number_id)
        response="Thank you for visiting! Our chatbot is currently under development and will be ready soon. We appreciate your patience and can't wait to assist you when it's up and running. If you need immediate help, please contact our support team. Thank you!"
        sendReply(response,phone_number_id,mobile,isBot)
        return {"message":"Not ready yet","status":True}
def getAnswer(theBot,message,phonenumber,waMessageId,phone_number_id):
    try:
        question= message
        isHistory = userChatHistory.objects[:1](title=phonenumber,category='whatsapp',chatbot_id=theBot['id']).first()
        if not isHistory:
            isHistory=userChatHistory(title=phonenumber,history=[],user_id=theBot['user_id'],chatbot_id=theBot['id'], category = 'whatsapp')
            isHistory.save()
        if int(theBot['questions'])>0:
            checkReminder(theBot)
            #embedding_function = OpenAIEmbeddings()
            #embedding_function = OpenAIEmbeddings()
        
           
            db4 = Chroma(client=client, collection_name=theBot['key'], embedding_function=embedding_function)
            
            token="500"

    # LLM
       
            prompt = ChatPromptTemplate(
                messages=[
                    SystemMessagePromptTemplate.from_template(
                        "You are a nice chatbot having a conversation with a human. Follow these guidelines closely:"
                        "Keep your response within a maximum of 25 words."
                        "Don't act like a third party conveying the message; be the company's own chatbot AI."
                        "You are a chatbot for"+theBot['name']+".Please stick to information provided about the company and avoid asnwering out of context qestions"
                        "Respond to the user like a human if they talk generally and do not make up context out of the provided one."
                        "If you don't have the answer, politely state that you don't know, avoiding fabricated responses."
                        "Employ bullet points solely when essential, such as for creating lists."
                        "Provide as much detail as possible in your response, even when context is limited."
                        "Avoid asking any follow-up questions to the customer."
                        "If user asks out of  the context relevancy please steer back to the to the company you provide information for"
                        "Context: {context}"
                    ),
                    HumanMessagePromptTemplate.from_template("{question}")
                ]
            )

            retriever = db4.as_retriever()

            memory=ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    


            qa_chain = ConversationalRetrievalChain.from_llm(
                llm,
                retriever=retriever, 
                # chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
                verbose=True,
                combine_docs_chain_kwargs={"prompt": prompt},
                #memory=memory
            )
            if len(isHistory.history)>0:
            #conversation({"question": "hi"})
                print("#1")
                my_history=[(  item['question'],  item['answer']) for item in isHistory.history[-3:]]
                chain_input = {"question": question, "chat_history": my_history}
                result = qa_chain(chain_input)
            else:
                print("#2")
                my_history=[(  item['question'],  item['answer']) for item in isHistory.history[-3:]]
                result = qa_chain({"question": question,"chat_history": my_history})


            saveData={}
            saveData['_id'] = ObjectId()
            saveData['waMessageId']=waMessageId
            saveData['phonenumberId'] =phone_number_id
            saveData['question'] = question
            saveData['answer'] = result['answer']
            saveData['created']=datetime.datetime.utcnow() 
            isHistory.history.append(saveData)
            isHistory.save()
            updateBot(theBot)
           
            return {'message':result['answer'] ,"status":True}
        else:
            return {'message': "Apologies, but I've reached my question limit for this session,please contact the administration!","status":True}
    except Exception as e: 
        
        return False
    

def updateBot(data):
    isBot = chatBots.objects[:1](user_id=data['user_id'],key=data['key']).first()
    if not isBot:
        return {"message": "chatBot does not exists","status":False}
    else:
        isBot.questions=isBot.questions-1
        isBot.save()
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
        else:
            return False    
    except Exception as e: 
        return make_response({'message': str(e),"status":False})     
def sendReply(message,phoneNumberId,tonumber,bot):
    url = "https://graph.facebook.com/v15.0/"+phoneNumberId+"/messages"
    payload = json.dumps({
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": tonumber,
    "type": "text",
    "text": {
        "preview_url": False,
        "body": message
    }
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization':'Bearer '+bot['whatsappData']['accessToken']
    }

    result=requests.request("POST", url, headers=headers, data=payload)
    print(result.content)


 
def markMessageRead(isBot,waMessageId,phone_number_id):
    url = "https://graph.facebook.com/v15.0/"+phone_number_id+"/messages"

    payload = json.dumps({
    "messaging_product": "whatsapp",
    "status": "read",
    "message_id": waMessageId
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization':'Bearer '+isBot['whatsappData']['accessToken']
    }

    requests.request("POST", url, headers=headers, data=payload)
    