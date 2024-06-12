from model.user import Users
from utils.passwordEncryption import encrypt_password, compare_passwords
from utils.sendMail import send_verification_email,send_reset_password_mail
from utils.JwtToken import generate_token
from flask import jsonify, make_response,Flask, render_template, request,session
import os
import datetime
import random
import string
charset = string.ascii_uppercase + string.digits


def verify_email(data):
    try:
        get_user=Users.objects[:1](verify_id=data['verify_id']).first() 
        if get_user:
           if (get_user.is_email_verified== False):
                   get_user.is_email_verified=True
                   get_user.save()
                   return {"message": "Email Verified Successfully","status":True}
           else:
               return {"message": "Email Already Verified Please Login","status":True}
        else:
            return {"message": "User not found!","status":True}   
    except Exception as e:
        return make_response({'message': str(e)}, 404)        
def google_login(data):
    try:
        user = Users.objects[:1](email=data['email']).first()
        if not user:
            user=Users(email=data['email'],type="google",google_id=data['google_id'],role="ADMIN",is_Active=True,is_email_verified=True,name=data['name'])
            user.save()
        if 'referal_code' not in user:
            random_string = ''.join(random.choice(charset) for _ in range(2))
            id=str(user.id)
            my_code=user.name[:3]+id[:3]+random_string
            user.referal_code=my_code.upper()
            user.save()
        if(user['is_Active']==True):
                    if(user['is_email_verified']==True):
                        payload = {"email": user['email'], "user_id": str(user['id']),"role":user['role'],"referal_code":user['referal_code']}
                        secret = os.environ.get('TOKEN_SECRET')
                        token = generate_token(payload, secret)
                        return make_response({'token': token,"status":True}, 200)
                    else:
                        return make_response({'message': 'Please Verify Your email before loging in !',"status":False})     
        else:
            return make_response({'message': 'User is Inactive Please Contact Administration!',"status":False})
    except Exception as e:
        return make_response({'message': str(e)}, 404)  
def facebook_login(data):
    try:
        user = Users.objects[:1](email=data['email']).first()
        if not user:
            user=Users(email=data['email'],type="facebook",facebook_id=data['facebook_id'],role="ADMIN",is_Active=True,is_email_verified=True,name=data['name'])
            user.save()
        if 'referal_code' not in user:
            random_string = ''.join(random.choice(charset) for _ in range(2))
            id=str(user.id)
            my_code=user.name[:3]+id[:3]+random_string
            user.referal_code=my_code.upper()
            user.save()
        if(user['is_Active']==True):
                    if(user['is_email_verified']==True):
                        payload = {"email": user['email'], "user_id": str(user['id']),"role":user['role'],"referal_code":user['referal_code']}
                        secret = os.environ.get('TOKEN_SECRET')
                        token = generate_token(payload, secret)
                        return make_response({'token': token,"status":True}, 200)
                    else:
                        return make_response({'message': 'Please Verify Your email before loging in !',"status":False})     
        else:
            return make_response({'message': 'User is Inactive Please Contact Administration!',"status":False})
    except Exception as e:
        return make_response({'message': str(e)}, 404)   
def update_referal_code(data):
        user = Users.objects[:1](id=data['id']).first()
        referal_code=Users.objects[:1](referal_code=data['refered_by'],id__ne=data['id']).first()
        if 'refered_by' not in user:
            if referal_code :
                user.refered_by=data['refered_by']
                user.save()
                return {"message": "Referal code added successfully!","status":True}
            else:
                return {"message": "Referal code not found!","status":False}
        else:
            return {"message": "Referal code already in use!","status":False}
def signup_service(userdata):
    try:
        email_check = Users.objects[:1](email=userdata['email'])
        if email_check:
            return {"message": "Email Already exists","status":False}
        else:
            name = userdata['name']
            email = userdata['email']
            # image = userdata['image']
            mobile = userdata['mobile']
            # address = userdata['address']
            role="ADMIN"
            if('refered_by' in userdata):
                refered_by=userdata['refered_by']
                user.refered_by=refered_by.upper()
            password = encrypt_password(userdata['password'])
            user = Users(name=name, email=email,
                        mobile=mobile, password=password,is_Active=1,role=role,is_email_verified=0,type="website")
            user.save()
            # content = "Please click the link below to verify Your Email:"
            random_string = ''.join(random.choice(charset) for _ in range(2))
            id=str(user.id)
            my_code=user.name[:3]+str(id[:3])+random_string
            user.referal_code=my_code.upper()
            
            user.save()
            mylink=os.environ.get('fronEndUrlMail')+"?token="+user.verify_id 
            # html = f"<h3>{content}</h3> <br>{link}"
            email_content = render_template(
                'email_verification_template.html',
                name=name,
                sitename="Infoapto",
                link=mylink
            )
            html=email_content
            subject = "Registration Successfull!"
            to_address = email
            receiver_username = name
            # Send the email and store the response
            send_verification_email(subject, html, to_address, receiver_username)
            return make_response({'message': 'Succesfully Created Please Verify The Email Sent To You!',"status":True}, 200)

    except Exception as e:
        return make_response({'message': str(e)}, 404)
def forget_password(data):
    try:
        email_check = Users.objects[:1](email=data['email'])
        if not email_check:
            return {"message": "Email does not exists","status":False}
        else:
            myuser=email_check[0]
            link=os.environ.get('fronEndUrlPassword')+"?token="+myuser.verify_id
            email_content = render_template(
                'password_reset_template.html',
                name=myuser.name,
                sitename="Infoapto",
                link=link
            )
            html=email_content
            subject = "Your link to reset password!"
            to_address = myuser.email
            receiver_username = myuser.name
            # Send the email and store the response
            send_reset_password_mail(subject, html, to_address, receiver_username)
            return make_response({'message': 'An email link has been sent to your registered mail follow the link for further process! ',"status":True}, 200)

    except Exception as e:
        return make_response({'message': str(e)}, 404)
def reset_password(data):
    try:
         email_check = Users.objects[:1](verify_id=data['verify_id'])
         if not email_check:
            return {"message": "Invalid Action","status":False}
         else:
            password = encrypt_password(data['password'])
            email_check.update(password=password.decode('utf-8'))
            return make_response({'message': 'Password reset successfully!',"status":True}, 200)
    except Exception as e:
        return make_response({'message': str(e)}, 404)
def change_password(data):
    try:
         email_check = Users.objects[:1](id=session['user_id']).first()
         if not email_check: 
            return {"message": "Invalid Action","status":False}
         else:
            if compare_passwords(data['oldPassword'],email_check['password']):
                password=encrypt_password(data['newPassword'])
                email_check.update(password=password.decode('utf-8'))
                return make_response({'message': 'Password reset successfully!',"status":True}, 200)
            else:
                return make_response({'message': 'Oldpassword Mismatch!',"status":True}, 200)
    except Exception as e:
       
        return make_response({'message': str(e)}, 404)
def login_service(user_credentials):
    try:
        email_check = Users.objects[:1](email=user_credentials['email'])

        if not email_check:
            return {"message": "Email does not exists","status":False}
        
        else:
            for user in email_check:
                if 'password' not in user:
                    return make_response({'message': 'Please set a password by using the forget password link below!',"status":False}) 
                if(user['role']=="ADMIN"):
                    if(user['is_Active']==True):
                        if(user['is_email_verified']==True):
                            if 'referal_code' not in user:
                                random_string = ''.join(random.choice(charset) for _ in range(2))
                                id=str(user.id)
                                my_code=user.name[:3]+id[:3]+random_string
                                user.referal_code=my_code.upper()
                                user.save()
                            payload = {"email": user['email'], "user_id": str(user['id']),"role":user['role'],"referal_code":user['referal_code']}
                            secret = os.environ.get('TOKEN_SECRET')
                            if compare_passwords(user_credentials['password'], user['password']):
                                token = generate_token(payload, secret)
                                return make_response({'token': token,"status":True}, 200)
                            else:
                                return make_response({'message': 'Invalid password',"status":False}, 200)
                        else:
                            return make_response({'message': 'Please Verify Your email before loging in !',"status":False})     
                    else:
                        return make_response({'message': 'User is Inactive Please Contact Administration!',"status":False})
            else:
                return make_response({'message': 'Invalid User',"status":False}, 200)
    except Exception as e:
        return make_response({'message': str(e)}, 404)      
def superadmin_login(data):
    try:
        user = Users.objects[:1](email=data['email']).first()
        if not user:
            return {"message": "Email does not exists","status":False}
        else:
            if(user['role']=="SUPERADMIN"):
                if(user['is_Active']==True):
                    if(user['is_email_verified']==True):
                        payload = {"email": user['email'], "user_id": str(user['id']),"role":user['role']}
                        secret = os.environ.get('TOKEN_SECRET')
                        if compare_passwords(data['password'], user['password']):
                            token = generate_token(payload, secret)
                            return make_response({'token': token,"status":True}, 200)
                        else:
                            return make_response({'message': 'Invalid password',"status":False}, 200)
                    else:
                        return make_response({'message': 'Please Verify Your email before loging in !',"status":False})     
                else:
                    return make_response({'message': 'User is Inactive Please Contact Administration!',"status":False})
            else:
                return make_response({'message': 'Invalid User',"status":False}, 403)
    except Exception as e:
        print(e)
        return make_response({'message': str(e)}, 404)   

def edit_user(editdata): 
    try:
        is_user = Users.objects[:1](id=editdata['id'])
        if not is_user:
            return {"message": "User does not exists","status":False}
        else:
            name = editdata['name']
            email = editdata['email']
            mobile = editdata['mobile']
            is_user.update(name=name,email=email,mobile=mobile,updated=datetime.datetime.utcnow)
            return make_response({'message': 'Succesfully Edited',"status":True}, 200)
    except Exception as e:
        return make_response({'message': str(e)}, 404)
def get_user(viewdata): 
    try:
        myResponse=[]
        
        is_user = Users.objects[:1](id=viewdata['id'])
        if not is_user:
            return {"message": "User does not exists","status":False}
        else: 
            for user in is_user:
                user_data = {}
                user_data['_id'] = str(user.id)
                user_data['name'] = user.name
                user_data['email'] = user.email
                user_data['mobile'] = user.mobile
                if 'refered_by' in user:
                    user_data['refered_by']=user.refered_by
                myResponse.append(user_data)
                if(len(myResponse)==1):
                    return make_response({"data":myResponse[0],"status":True}, 200)
                else:
                    return make_response({"data":myResponse,"status":True}, 200)    
    except Exception as e:
       
        return make_response({'message': str(e)}, 404)

def update_userStatus(viewdata): 
    try:
        is_user = Users.objects[:1](id=viewdata['id'])
        if not is_user:
            return {"status": False, "message": "User does not exists"}
        else: 
            if(is_user.is_Active==0):
                is_user.update(is_Active=1)
                return make_response({"message":"User Changed to Active","status":True}, 200)   
            else:
                is_user.update(is_Active=0)    
                return make_response({"message":"User Changed to Inactive","status":True}, 200)         
    except Exception as e:
      
        return make_response({'message': str(e)}, 404)    