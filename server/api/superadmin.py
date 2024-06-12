from flask import Blueprint, request
su_route = Blueprint('su_route', __name__)
from utils.JwtToken import validate_token_superadmin 

from services.user_service import superadmin_login,change_password

from services.superadmin_services import view_all_transactions,get_all_users,view_transaction,add_plans,view_all_plans,edit_plan,change_plan_status,view_plan,toggle_user_status


@su_route.route("/api/v1/su/superadminLogin", methods=['POST'])
def superadminLogin():
    data = request.get_json()
    return superadmin_login(data)


@su_route.route("/api/v1/su/viewAllTransactions", methods=['POST'])
@validate_token_superadmin
def viewAllTransactions():
    data = request.get_json()
    return view_all_transactions(data)

@su_route.route("/api/v1/su/getAllUsers", methods=['POST'])
@validate_token_superadmin
def getAllUsers():
    data = request.get_json()
    return get_all_users(data)

@su_route.route("/api/v1/su/viewTransaction", methods=['POST'])
@validate_token_superadmin
def viewTransaction():
    data = request.get_json()
    return view_transaction(data)

@su_route.route("/api/v1/su/addPlans", methods=['POST'])
@validate_token_superadmin
def addPlans():
    data = request.get_json()
    return add_plans(data)

@su_route.route("/api/v1/su/viewAllPlans", methods=['POST'])
@validate_token_superadmin
def viewAllPlans():
    data = request.get_json()
    return view_all_plans(data)
@su_route.route("/api/v1/su/editPlan", methods=['POST'])
@validate_token_superadmin
def editPlan():
    data = request.get_json()
    return edit_plan(data)
@su_route.route("/api/v1/su/changePlanStatus", methods=['POST'])
@validate_token_superadmin
def changePlanStatus():
    data = request.get_json()
    return change_plan_status(data)
@su_route.route("/api/v1/su/viewPlan", methods=['POST'])
@validate_token_superadmin
def viewPlan():
    data = request.get_json()
    return view_plan(data)
@su_route.route("/api/v1/su/toggleUserStatus", methods=['POST'])
@validate_token_superadmin
def toggleUserStatus():
    data = request.get_json()
    return toggle_user_status(data)
@su_route.route("/api/v1/su/changePassword", methods=['POST'])
@validate_token_superadmin
def changePassword():
    data = request.get_json()
    return change_password(data)