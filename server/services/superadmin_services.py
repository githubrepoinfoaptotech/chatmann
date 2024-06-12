from model.user import Users
from flask import jsonify, make_response,Flask, render_template, request,session
from model.user_invoice import User_invoices
from model.user_transaction import User_transactions
from model.plan import Plans
import datetime


def get_all_users(viewdata): 
    try:
        myResponse=[]
        if viewdata['page']:
            page=viewdata['page']
        else:
            page=0  
        per_page=10      
        skip = (page - 1) * per_page
        is_user = Users.objects(role="ADMIN").skip(skip).limit(per_page)
        total_count = Users.objects(role="ADMIN").count()
        if not is_user:
            return {"status": False, "message": "No Users Found"}
        else: 
            
            for user in is_user:
                user_data = {}
                user_data['_id'] = str(user.id)
                user_data['name'] = user.name
                user_data['email'] = user.email
                user_data['mobile'] = user.mobile
                user_data['is_Active']=user.is_Active
                user_data['referal_code']=user.referal_code
                user_data['refered_by']=user.refered_by
                myResponse.append(user_data)          
        return make_response({"data":myResponse,"count":total_count,"status":True}, 200)         
    except Exception as e:
       
        return make_response({'message': str(e)}, 404)
def view_all_transactions(userdata):
    try:
        myResponse=[]
        refered_by=""
        if userdata['page']:
            page=userdata['page']
        else:
            page=0  
        per_page=10      
        skip = (page - 1) * per_page
        today_date = datetime.datetime.now()
        if 'fromDate' in userdata and (userdata['fromDate']):
            from_date = datetime.datetime.strptime(userdata['fromDate'], '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            from_date = today_date.replace(hour=0, minute=0, second=0, microsecond=0)
        if 'toDate' in userdata and (userdata['toDate']):
            to_date = datetime.datetime.strptime(userdata['toDate'], '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999)  
        else: 
            to_date = today_date.replace(hour=23, minute=59, second=59, microsecond=999)
        if 'refered_by' in userdata and (userdata['refered_by']):
            refered_by=userdata['refered_by']
        query = {
        'created__gte': from_date,
        'created__lte': to_date
        }
        if refered_by:
            query['refered_by']=refered_by
        data=User_invoices.objects(**query).skip(skip).limit(per_page)
        total_count = User_invoices.objects(**query).count()
        myResponse.extend([{'_id':str(transaction_data.id),'user_id': str(transaction_data.user_id), 'total_amount': transaction_data.total_amount, 'basic_amount': transaction_data.basic_amount, 'tax_percentage': transaction_data.tax_percentage, 'total_tax_values': transaction_data.total_tax_values, 'cgst': transaction_data.cgst,'sgst': transaction_data.sgst, 'invoice_number': transaction_data.invoice_number,'payment_details': transaction_data.payment_details,'refered_by':transaction_data['refered_by'] ,'created': transaction_data.created} for transaction_data in data])
        return make_response({"data":myResponse,"count":total_count,"status":True}, 200)
    except Exception as e:
       
        return make_response({'message': str(e)}, 404) 
def view_transaction(userdata):
    try:
        myResponse={}
        transaction_data=User_invoices.objects(id=userdata['id']).first()
        myResponse={'_id':str(transaction_data.id),'user_id': str(transaction_data.user_id), 'total_amount': transaction_data.total_amount, 'basic_amount': transaction_data.basic_amount, 'tax_percentage': transaction_data.tax_percentage, 'total_tax_values': transaction_data.total_tax_values, 'cgst': transaction_data.cgst,'sgst': transaction_data.sgst, 'invoice_number': transaction_data.invoice_number,'payment_details': transaction_data.payment_details, 'created': transaction_data.created}
        return make_response({"data":myResponse,"status":True}, 200)
    except Exception as e:
       
        return make_response({'message': str(e)}, 404) 
def add_plans(data):
    #title,amount,desc,country_code,type,currency,taxp_perc,no.Question,no.characters
    try:
        plan_data=Plans.objects(country_code=data['country_code'])
        if(len(plan_data)>0): 
            myNum=set_planNumber(len(plan_data)+1)
            plan_code="PLN"+data['country_code']+myNum
            create_plan=Plans(title=data['title'],price=data['price'],about=data['about'],country_code=data['country_code'],currency=data['currency'],tax_perc=data['tax_perc'],questions=data['questions'],token_limit=data['token_limit'],plan_order=len(plan_data)+1,validity="30",isActive=1,plan_code=plan_code)
            create_plan.save()
            return make_response({"message":"Plan added successfully","status":True}, 200) 
        else:
            plan_code="PLN"+data['country_code']+"0000"
            create_plan=Plans(title=data['title'],price=data['price'],about=data['about'],country_code=data['country_code'],currency=data['currency'],tax_perc=data['tax_perc'],questions=data['questions'],token_limit=data['token_limit'],plan_order=1,validity="30",isActive=1,plan_code=plan_code)
            create_plan.save()
            return make_response({"message":"Plan added successfully","status":True}, 200) 
    except Exception as e:
        return make_response({'message': str(e)}, 404) 
def view_all_plans(data):
    try:
        query={}
        myResponse=[]
        if data['page']:
            page=data['page']
        else:
            page=0  
        per_page=10      
        skip = (page - 1) * per_page
        if(('country_code' in data) and (data['country_code'])):
            plan_data=Plans.objects(country_code=data['country_code']).skip(skip).order_by('plan_order').limit(per_page)
            total_count = Plans.objects(country_code=data['country_code']).count()
        else: 
            plan_data=Plans.objects().skip(skip).order_by('-created').limit(per_page)
            total_count = Plans.objects().count()
        myResponse.extend([{'_id': str(plan.id), 'price': plan.price, 'isActive':plan.isActive,'about': plan.about,'validity': plan.validity,  'title': plan.title, 'questions': plan.questions, 'tax_perc':plan.tax_perc,'currency':plan.currency,'country_code':plan.country_code,'token_limit': plan.token_limit,'plan_order':plan.plan_order,  'created': plan.created} for plan in plan_data]) 
        return make_response({"data":myResponse,"count":total_count,"status":True}, 200)
    except Exception as e:
        return make_response({'message': str(e)}, 404)


def edit_plan(data):
    try:
        plan_data=Plans.objects(id=data['id']).first()
        if plan_data:
            plan_data.update(title=data['title'],price=data['price'],about=data['about'],currency=data['currency'],tax_perc=data['tax_perc'],questions=data['questions'],token_limit=data['token_limit'],country_code=data['country_code'],plan_order=data['plan_order'])
            plan_data.save()
            return make_response({"message":"Edit successfull","status":True}, 200) 
        else:
            return make_response({"message":"Invalid Plan","status":False}, 200) 
    except Exception as e:
        return make_response({'message': str(e)}, 404)
def change_plan_status(data):
    try:
        plan_data=Plans.objects(id=data['id']).first()
        plan_data.isActive= not  plan_data.isActive
        plan_data.save()
        if(plan_data.isActive==True):
            return make_response({"message":"Changed to active","status":True}, 200) 
        else:
            return make_response({"message":"Changed to Inactive","status":True}, 200) 
    except Exception as e:
        return make_response({'message': str(e)}, 404)


def view_plan(data):
    try:
        plan=Plans.objects(id=data['id']).first()
        if plan:
            data={'_id': str(plan.id), 'price': plan.price, 'isActive':plan.isActive,'about': plan.about,'validity': plan.validity,  'title': plan.title, 'questions': plan.questions, 'tax_perc':plan.tax_perc,'currency':plan.currency,'country_code':plan.country_code,'token_limit': plan.token_limit,'plan_order':plan.plan_order, 'created': plan.created} 
            return make_response({"data":data,"status":True}, 200) 
        else:
            return make_response({"message":"Not found","status":False}, 200) 
    except Exception as e:
        return make_response({'message': str(e)}, 404)
def toggle_user_status(data):
    try:
        user_data=Users.objects(id=data['id']).first()
        user_data.is_Active= not  user_data.is_Active
        user_data.save()
        if(user_data.is_Active==True):
            return make_response({"message":"Changed to active","status":True}, 200) 
        else:
            return make_response({"message":"Changed to Inactive","status":True}, 200) 
    except Exception as e:
        return make_response({'message': str(e)}, 404)
def set_planNumber(i):
    i=int(i)
    if(i<9) :
        invInt="0000"+str(i)
    elif (i>=999):
        invInt="0"+str(i)
    elif (i>=99):
        invInt="00"+str(i)
    elif (i>=9):
        invInt="000"+str(i)
    else:
        invInt=i
    return invInt