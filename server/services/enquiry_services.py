from model.enquiry import Enquiry
from flask import jsonify, make_response,session,Flask, render_template, request
def enquiry(data):
    try:
        theBot=session['myBot']
        myenquiry=Enquiry(chatbot_id=theBot['id'],name=data['name'],email=data['email'],mobile=data['mobile'],message=data['message'])
        myenquiry.save()
        return {"message": "Enquiry Raised","status":True}
    except Exception as e:
            return make_response({'message': str(e)}, 404) 
def getAllEnquiry(data):
    try:
        per_page=10 
        if data['page']:
            page=data['page']  
            if(page>0):
              skip = (page - 1) * per_page
            else:
              skip=0
        else:
            page=0  
            skip = 0
            
        myResponse=[] 
        
        #skip = (page - 1) * per_page
        enquiry_datas=Enquiry.objects(chatbot_id=data['chatBotId']).skip(skip).limit(per_page)
        total_count=Enquiry.objects(chatbot_id=data['chatBotId']).count()
        myResponse.extend([{'_id':str(enquiry_data.id),'name': enquiry_data.name,'email': enquiry_data.email,'mobile': enquiry_data.mobile,'created': enquiry_data.created,'message':enquiry_data.message} for enquiry_data in enquiry_datas])
        return make_response({"data":myResponse,"count":total_count,"status":True}, 200)
    except Exception as e:
            return make_response({'message': str(e)}, 404) 