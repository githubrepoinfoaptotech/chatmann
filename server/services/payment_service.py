from model.user_transaction import User_transactions
from model.plan import Plans
from model.user_invoice import User_invoices
from model.user import Users
from model.chatbot import chatBots
from flask import jsonify, make_response,session,render_template
import os
import datetime
from datetime import timedelta
import razorpay
from mongoengine import Q
from utils.sendMail import send_invoice
import pdfkit
def initiate_transaction(transaction_data):
    try:
        plan_data=Plans.objects[:1](id=transaction_data['plan_id']).first()
        print(plan_data.tax_perc)
        if plan_data:
            transaction_details={}
            user_id=session['user_id']
            price=plan_data.price
            plan_id=transaction_data['plan_id']
            status="Pending"
            # Gstpercentage = int(os.environ.get('Gstpercentage'))
            currency=plan_data.currency
            GstAmount = (price * plan_data.tax_perc)/100
            total_amount =price +GstAmount
            userTransaction = User_transactions(user_id=user_id,plan_id=plan_id,status=status,total_amount=total_amount,currency=currency,chatbot_id=transaction_data['chatbot_id'])
            userTransaction.save()
            transaction_details['id']=str(userTransaction.id)   
            transaction_details['total_amount']=userTransaction.total_amount*100
            transaction_details['currency']=userTransaction.currency
            order=razorPayInitiate(transaction_details)
            userTransaction.update(order_id=order['id'])
            return {"order_id":order,"status":True}
        else:
            return {"message": "Plan Not Found","status":False}    
    except Exception as e:
       
        return make_response({'message': str(e)}, 404)     
def get_PaymentSuccess(success_data):
    # Initialize the Razorpay client with your API key and secret key
    client = razorpay.Client(auth=(os.environ.get('razor_key'), os.environ.get('razor_secret')))

    # Replace 'YOUR_PAYMENT_ID' with the actual payment ID you want to retrieve details for
    payment_id = success_data['razorpay_payment_id']
    try:
        current_year = datetime.datetime.now().year
        # Fetch payment details using the payment ID
        payment = client.payment.fetch(payment_id)
        transaction_data=User_transactions.objects[:1](order_id=success_data['razorpay_order_id']).first()
        plan_data=Plans.objects[:1](id=transaction_data['plan_id']).first()
        invoice_data=User_invoices.objects[:1](user_id=transaction_data['user_id']).order_by('-inv_int').first() 
        user_data=Users.objects[:1](id=transaction_data['user_id']).first() 
        if 'refered_by' in user_data:
            refered_by=user_data.refered_by
        else:
            refered_by=""
        if invoice_data:
            intInc=int(invoice_data["inv_int"])+1 
            inv_int=set_invoiceNumber(intInc)
            newInv="INV-"+str(current_year)+str(inv_int)
            create_user_invoice=User_invoices(chatbot_id=transaction_data['chatbot_id'],user_id=transaction_data['user_id'],transaction_id=transaction_data['id'],total_amount=transaction_data['total_amount'],basic_amount=plan_data['price'],tax_percentage=plan_data.tax_perc,total_tax_values=plan_data['price']-transaction_data['total_amount'],cgst=plan_data.tax_perc/2,sgst=plan_data.tax_perc/2,invoice_number=newInv,year=str(current_year),inv_int=intInc,plan_id=plan_data['id'],payment_details=payment,refered_by=refered_by)
            create_user_invoice.save()
            transaction_data.update(status='paid')
            updateChatBot(transaction_data['chatbot_id'],plan_data)
            bot_data=chatBots.objects[:1](id=transaction_data['chatbot_id']).first()
            # Parse the input datetime string
            thedate_input_datetime=datetime.datetime.strptime(str(create_user_invoice.created), '%Y-%m-%d %H:%M:%S.%f')
            start_input_datetime = datetime.datetime.strptime(str(bot_data.validityStartDate), '%Y-%m-%d %H:%M:%S.%f')
            end_input_datetime=datetime.datetime.strptime(str(bot_data.validityEndDate), '%Y-%m-%d %H:%M:%S.%f')
            # Format the datetime as 'YYYY-MM-DD'
            start_date = start_input_datetime.strftime('%Y-%m-%d')
            endate = end_input_datetime.strftime('%Y-%m-%d')
            sub_date=thedate_input_datetime.strftime('%Y-%m-%d')
            email_content = render_template(
                'invoice_template.html',
                customer_name=user_data.name,
                sitename="Chatmann",
                customer_email=user_data.email,
                invoice_number=create_user_invoice.invoice_number,
                total_amount=create_user_invoice.total_amount,
                total=create_user_invoice.total_amount,
                date=sub_date,
                start_date=start_date,
                end_date=endate,
                subscription_plan=plan_data.title,
                plan_description=plan_data.about,
                currency=transaction_data.currency,
                payment_method=create_user_invoice.payment_details['method']
            )
            invoice_content={
                "customer_name":user_data.name,
                "sitename":"Chatmann",
                "customer_email":user_data.email,
                "invoice_number":create_user_invoice.invoice_number,
                "total_amount":create_user_invoice.total_amount,
                "total":create_user_invoice.total_amount,
                "date":sub_date,
                "start_date":start_date,
                "end_date":endate,
                "subscription_plan":plan_data.title,
                "plan_description":plan_data.about,
                "currency":transaction_data.currency,
                "payment_method":create_user_invoice.payment_details['method']
            }
            with open('templates/invoice_template.html', 'r') as file:
               template = file.read()
            print("#done1")
            # Replace placeholders in the template with actual data
            for key, value in invoice_content.items():
                template = template.replace('{{' + key + '}}', str(value))
            print("#done2")
            # Convert HTML to PDF
            pdfkit.from_string(template, "assets/invoices/"+str(create_user_invoice.invoice_number)+'.pdf')
            print("#done3")
            html =email_content
            subject = "Your invoice for subscription."
            to_address = user_data.email
            receiver_username = user_data.name
            attachment="assets/invoices/"+str(create_user_invoice.invoice_number)+'.pdf'
            send_invoice(subject, html, to_address, receiver_username,attachment)
        else:
            intInc=1 
            inv_int=set_invoiceNumber(intInc)
            newInv="INV-"+str(current_year)+str(inv_int)
            create_user_invoice=User_invoices(chatbot_id=transaction_data['chatbot_id'],user_id=transaction_data['user_id'],transaction_id=transaction_data['id'],total_amount=transaction_data['total_amount'],basic_amount=plan_data['price'],tax_percentage=plan_data.tax_perc,total_tax_values=plan_data['price']-transaction_data['total_amount'],cgst=plan_data.tax_perc/2,sgst=plan_data.tax_perc/2,invoice_number=newInv,year=str(current_year),inv_int=intInc,plan_id=plan_data['id'],payment_details=payment,refered_by=refered_by)
            create_user_invoice.save()   
            transaction_data.update(status='paid')
            updateChatBot(transaction_data['chatbot_id'],plan_data)
            bot_data=chatBots.objects[:1](id=transaction_data['chatbot_id']).first()
            # Parse the input datetime string
            thedate_input_datetime=datetime.datetime.strptime(str(create_user_invoice.created), '%Y-%m-%d %H:%M:%S.%f')
            start_input_datetime = datetime.datetime.strptime(str(bot_data.validityStartDate), '%Y-%m-%d %H:%M:%S.%f')
            end_input_datetime=datetime.datetime.strptime(str(bot_data.validityEndDate), '%Y-%m-%d %H:%M:%S.%f')
            # Format the datetime as 'YYYY-MM-DD'
            start_date = start_input_datetime.strftime('%Y-%m-%d')
            endate = end_input_datetime.strftime('%Y-%m-%d')
            sub_date=thedate_input_datetime.strftime('%Y-%m-%d')
            email_content = render_template(
                'invoice_template.html',
                customer_name=user_data.name,
                sitename="Chatmann",
                customer_email=user_data.email,
                invoice_number=create_user_invoice.invoice_number,
                total_amount=create_user_invoice.total_amount,
                total=create_user_invoice.total_amount,
                date=sub_date,
                start_date=start_date,
                end_date=endate,
                subscription_plan=plan_data.title,
                plan_description=plan_data.about,
                currency=transaction_data.currency,
                payment_method=create_user_invoice.payment_details['method']
            )
            invoice_content={
                "customer_name":user_data.name,
                "sitename":"Chatmann",
                "customer_email":user_data.email,
                "invoice_number":create_user_invoice.invoice_number,
                "total_amount":create_user_invoice.total_amount,
                "total":create_user_invoice.total_amount,
                "date":sub_date,
                "start_date":start_date,
                "end_date":endate,
                "subscription_plan":plan_data.title,
                "plan_description":plan_data.about,
                "currency":transaction_data.currency,
                "payment_method":create_user_invoice.payment_details['method']
            }
            with open('templates/invoice_template.html', 'r') as file:
               template = file.read()
            print("#done1")
            # Replace placeholders in the template with actual data
            for key, value in invoice_content.items():
                 template = template.replace('{{' + key + '}}', str(value))
            print("#done2")
            # Convert HTML to PDF
            pdfkit.from_string(template, "assets/invoices/"+str(create_user_invoice.invoice_number)+'.pdf')
            print("#done3")
            html =email_content
            subject = "Your invoice for subscription."
            to_address = user_data.email
            receiver_username = user_data.name
            attachment="assets/invoices/"+str(create_user_invoice.invoice_number)+'.pdf'
            send_invoice(subject, html, to_address, receiver_username,attachment)
        # Access payment details
        return {"message":"Upgraded Successfully","status":True}
    except Exception as e:
        print(e)
        return {'message': str(e),"status":False}

def razorPayInitiate(transaction_details):
    # Initialize Razorpay client with your API Key and Secret Key
    client = razorpay.Client(auth=(os.environ.get('razor_key'), os.environ.get('razor_secret')))
    # Create a payment order
    order_amount = int(transaction_details['total_amount']) # Amount in paise (e.g., 50000 paise = ₹500)
    order_currency = transaction_details['currency']
    order_receipt = transaction_details['id']  # You should generate a unique receipt ID

    order = client.order.create({
        "amount": order_amount,
        "currency": order_currency,
        "receipt": order_receipt
    })

    # Get the order ID from the response
      
    return order

def view_all_plans():
    try:
        if session['country_code'] == None:
            return {"message": "Something went wrong","status":False}
        myResponse=[]
        my_plans=Plans.objects(country_code=session['country_code']).order_by("plan_order")
        if not my_plans:
            return {"message": "Plans Not Found","status":False}
        else:
            myResponse.extend([{'_id': str(plan.id), 'price': plan.price, 'currency':plan.currency,'about': plan.about,'validity': plan.validity, 'title': plan.title, 'questions': plan.questions, 'token_limit': plan.token_limit, 'created': plan.created} for plan in my_plans])      
            # myResponse.insert(0, myResponse.pop())    
            return make_response({"data":myResponse,"status":True}, 200)        
    except Exception as e:
        return make_response({'message': str(e)}, 404)    
def set_invoiceNumber(i):
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
def updateChatBot(chatbot_id,plan):
    try:
        bot_data=chatBots.objects[:1](id=chatbot_id).first()
        current_date = datetime.datetime.utcnow() 
        new_date = current_date + timedelta(days=30)
       
        if bot_data['validityEndDate'] is None:
            print("#1")
            bot_data.questions = int(plan['questions'])
            bot_data.allowed_characters = int(plan['token_limit'])
            bot_data.validityStartDate = current_date
            bot_data.validityEndDate = new_date
            bot_data.plan_id=plan['id']
            bot_data.plan_name=plan['title']
            bot_data.save()
        elif  bot_data['validityEndDate'] < current_date:
            print("#2")
            bot_data.questions = bot_data.questions+int(plan['questions'])
            bot_data.allowed_characters = int(plan['token_limit'])
            bot_data.validityStartDate = current_date
            bot_data.validityEndDate = new_date
            bot_data.plan_id=plan['id']
            bot_data.plan_name=plan['title']
            bot_data.save()
        else:
            print("#3")
            bot_data.questions = bot_data.questions+int(plan['questions'])
            bot_data.validityEndDate =bot_data.validityEndDate + timedelta(days=30)
            bot_data.allowed_characters = int(plan['token_limit'])
            bot_data.plan_id=plan['id']
            bot_data.plan_name=plan['title']
            bot_data.save()
        print(bot_data)
        return True
    except Exception as e:
        print(e)
        return False
def view_all_transactions(userdata):
    try:
        myResponse=[]
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
        if 'toDate' in userdata and  (userdata['toDate']):
            to_date = datetime.datetime.strptime(userdata['toDate'], '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999)  
        else: 
            to_date = today_date.replace(hour=23, minute=59, second=59, microsecond=999)
        query = {
        'user_id': session['user_id'],
        'chatbot_id': userdata['chatbot_id'],
        'created__gte': from_date,
        'created__lte': to_date
         }
        data=User_invoices.objects(**query).skip(skip).limit(per_page)
        total_count = User_invoices.objects(**query).count()
        myResponse.extend([{'_id':str(transaction_data.id),'user_id': str(transaction_data.user_id), 'total_amount': transaction_data.total_amount, 'basic_amount': transaction_data.basic_amount, 'tax_percentage': transaction_data.tax_percentage, 'total_tax_values': transaction_data.total_tax_values, 'cgst': transaction_data.cgst,'sgst': transaction_data.sgst, 'invoice_number': transaction_data.invoice_number,'payment_details': transaction_data.payment_details, 'created': transaction_data.created} for transaction_data in data])
        return make_response({"data":myResponse,"count":total_count,"status":True}, 200)
    except Exception as e:
       
        return make_response({'message': str(e)}, 404) 
def view_transaction(userdata):
    try:
        myResponse={}
        transaction_data=User_invoices.objects(user_id=session['user_id'],id=userdata['id']).first()
        myResponse={'_id':str(transaction_data.id),'user_id': str(transaction_data.user_id), 'total_amount': transaction_data.total_amount, 'basic_amount': transaction_data.basic_amount, 'tax_percentage': transaction_data.tax_percentage, 'total_tax_values': transaction_data.total_tax_values, 'cgst': transaction_data.cgst,'sgst': transaction_data.sgst, 'invoice_number': transaction_data.invoice_number,'payment_details': transaction_data.payment_details ,'created': transaction_data.created}
        return make_response({"data":myResponse,"status":True}, 200)
    except Exception as e:
       
        return make_response({'message': str(e)}, 404) 