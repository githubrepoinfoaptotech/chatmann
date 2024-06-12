from flask import Blueprint, request
from services.user_service import signup_service,login_service,edit_user,get_user,update_userStatus,verify_email,forget_password,reset_password,change_password
from services.user_service import google_login,facebook_login,update_referal_code
user_route = Blueprint('user_route', __name__)
from utils.JwtToken import validate_token_admin

@user_route.route("/api/v1/user/signup", methods=['POST'])
def signup():
    data = request.get_json()
    return signup_service(data)

@user_route.route("/api/v1/user/login", methods=['POST'])
def login():
    data = request.get_json()
    return login_service(data)
@user_route.route("/api/v1/user/googleLogin", methods=['POST'])
def googleLogin():
    data = request.get_json()
    return google_login(data)
@user_route.route("/api/v1/user/facebookLogin", methods=['POST'])
def facebookLogin():
    data = request.get_json()
    return facebook_login(data)


@user_route.route("/api/v1/user/verifyEmail", methods=['POST'])
def verifyEmail():
    data = request.get_json()
    return verify_email(data)

@user_route.route("/api/v1/user/forgetPassword", methods=['POST'])
def forgetPassword():
    data = request.get_json()
    return forget_password(data)

@user_route.route("/api/v1/user/resetPassword", methods=['POST'])
def resetPassword():
    data = request.get_json()
    return reset_password(data)


@user_route.route("/api/v1/user/changePassword", methods=['POST'])
@validate_token_admin
def changePassword():
    data = request.get_json()
    return change_password(data)

@user_route.route("/api/v1/user/updateReferalCode", methods=['POST'])
@validate_token_admin
def updateReferalCode():
    data = request.get_json()
    return update_referal_code(data)

@user_route.route("/api/v1/user/editUser", methods=['POST'])
@validate_token_admin
def editUser():
    data = request.get_json()
    return edit_user(data)

@user_route.route("/api/v1/user/getUser", methods=['POST'])
@validate_token_admin
def getUser():
    data = request.get_json() 
    return get_user(data)


@user_route.route("/api/v1/user/updateUserStatus", methods=['POST'])
@validate_token_admin
def updateUserStatus():
    data = request.get_json() 
    return update_userStatus(data)